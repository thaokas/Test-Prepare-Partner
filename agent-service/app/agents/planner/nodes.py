"""Planner Agent 节点函数"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import httpx
from langchain_core.messages import HumanMessage, AIMessage
from app.llm import get_chat_model, get_vision_model
from app.tools.search_tools import search_exam_info
from app.tools.db_tools import create_study_plan
from app.agents.planner.prompts import (
    PARSE_INPUT_PROMPT,
    CHECK_FIELDS_PROMPT,
    PARSE_REPLY_PROMPT,
    GENERATE_PLAN_PROMPT,
    RESOURCE_SUMMARY_PROMPT,
    get_foundation_level_desc,
)

logger = logging.getLogger(__name__)

# ── 常量：估算完成备考所需最少天数的基准 ──────────────────────────────
# 假设备考总量约 200 个学习单元（每单元 75 分钟），作为启发式估算
_TOTAL_STUDY_UNITS = 200
_UNIT_MINUTES = 75


async def calculate_study_time_node(state: Dict) -> Dict:
    """计算备考时间分配：总天数、阶段划分、预计完成日期（纯计算节点）"""
    try:
        exam_date = datetime.strptime(state["exam_date"], "%Y-%m-%d").date()
        today = date.today()
        total_days = (exam_date - today).days

        if total_days <= 0:
            return {
                "total_days": 0,
                "phases": [],
                "estimated_completion_date": str(exam_date),
                "error": "考试日期已过或为今天",
            }

        phases: List[Dict] = []
        cursor = today
        remaining = total_days

        # 基础阶段：剩余超过 90 天的部分
        if remaining > 90:
            foundation_days = remaining - 90
            foundation_end = cursor + timedelta(days=foundation_days - 1)
            phases.append({
                "phase": 1,
                "phase_name": "基础阶段",
                "start_date": str(cursor),
                "end_date": str(foundation_end),
                "days": foundation_days,
            })
            cursor = foundation_end + timedelta(days=1)
            remaining = 90

        # 强化阶段：剩余 31-90 天
        if remaining > 30:
            reinforcement_days = remaining - 30
            reinforcement_end = cursor + timedelta(days=reinforcement_days - 1)
            phases.append({
                "phase": 2,
                "phase_name": "强化阶段",
                "start_date": str(cursor),
                "end_date": str(reinforcement_end),
                "days": reinforcement_days,
            })
            cursor = reinforcement_end + timedelta(days=1)
            remaining = 30

        # 冲刺阶段：最后 ≤30 天
        sprint_end = exam_date - timedelta(days=1)
        if cursor <= sprint_end:
            phases.append({
                "phase": 3,
                "phase_name": "冲刺阶段",
                "start_date": str(cursor),
                "end_date": str(sprint_end),
                "days": (sprint_end - cursor).days + 1,
            })

        # 预估能否在考试日前完成备考
        daily_hours = state.get("daily_hours") or 2.0
        rest_days_per_week = state.get("rest_days_per_week") or 1
        effective_study_days_ratio = (7 - rest_days_per_week) / 7
        units_per_day = (daily_hours * 60) / _UNIT_MINUTES
        min_days = max(
            int(_TOTAL_STUDY_UNITS / (units_per_day * effective_study_days_ratio)),
            30,  # 至少备考 30 天
        )

        if min_days < total_days:
            completion_date = today + timedelta(days=min_days)
            # 不超过考试日
            estimated_completion_date = str(min(completion_date, exam_date - timedelta(days=1)))
        else:
            estimated_completion_date = str(exam_date)

        return {
            "total_days": total_days,
            "phases": phases,
            "estimated_completion_date": estimated_completion_date,
        }
    except Exception as e:
        logger.error(f"calculate_study_time_node error: {e}")
        return {
            "total_days": 90,
            "phases": [{"phase": 1, "phase_name": "基础阶段",
                        "start_date": str(date.today()),
                        "end_date": str(date.today() + timedelta(days=89)),
                        "days": 90}],
            "estimated_completion_date": state.get("exam_date", ""),
            "error": str(e),
        }


def _extract_json(text: str) -> Dict:
    """从 LLM 响应文本中提取 JSON（去除 markdown 代码块）"""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        # 取第一个代码块内容
        text = parts[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


async def parse_input_node(state: Dict) -> Dict:
    """解析用户初始输入，提取考试信息字段（LLM 节点）"""
    try:
        messages = state.get("messages", [])
        last_human = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
            ""
        )

        prompt = PARSE_INPUT_PROMPT.format(
            message=last_human,
            resource_summary=state.get("resource_summary", "（无资料）"),
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        data = _extract_json(response.content if isinstance(response.content, str) else str(response.content))

        updates: Dict = {}
        for field in ("exam_name", "exam_type", "exam_date", "daily_hours",
                      "foundation_level", "weak_subjects", "rest_days_per_week"):
            val = data.get(field)
            if val is not None:
                updates[field] = val

        # 合并 URL 列表（去重）
        existing_urls = state.get("urls", [])
        existing_pdf = state.get("pdf_urls", [])
        existing_img = state.get("image_urls", [])
        new_urls = [u for u in data.get("urls", []) if u not in existing_urls]
        new_pdf = [u for u in data.get("pdf_urls", []) if u not in existing_pdf]
        new_img = [u for u in data.get("image_urls", []) if u not in existing_img]
        if new_urls or existing_urls:
            updates["urls"] = existing_urls + new_urls
        if new_pdf or existing_pdf:
            updates["pdf_urls"] = existing_pdf + new_pdf
        if new_img or existing_img:
            updates["image_urls"] = existing_img + new_img

        return updates
    except Exception as e:
        logger.error(f"parse_input_node error: {e}")
        return {"error": str(e)}


async def _summarize_text(text: str) -> str:
    """用 LLM 将文本压缩为不超过 300 字的摘要"""
    prompt = RESOURCE_SUMMARY_PROMPT.format(content=text[:4000])
    llm = get_chat_model()
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    return response.content if isinstance(response.content, str) else str(response.content[0])


async def analyze_resources_node(state: Dict) -> Dict:
    """抓取网页/PDF/图片资料，生成统一的 resource_summary（Tool 节点）"""
    urls = state.get("urls", [])
    pdf_urls = state.get("pdf_urls", [])
    image_urls = state.get("image_urls", [])

    if not urls and not pdf_urls and not image_urls:
        return {"resource_summary": ""}

    summaries: List[str] = []

    # 处理网页 URL
    for url in urls[:3]:  # 最多处理 3 个
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                # 移除 script/style
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                text = soup.get_text(separator="\n", strip=True)
                summary = await _summarize_text(text)
                summaries.append(f"[网页资料] {summary}")
        except Exception as e:
            logger.warning(f"analyze_resources: failed to fetch {url}: {e}")

    # 处理 PDF URL
    for pdf_url in pdf_urls[:3]:
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(pdf_url)
                resp.raise_for_status()
                import io
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(resp.content))
                text = "\n".join(
                    page.extract_text() or "" for page in reader.pages[:20]
                )
                summary = await _summarize_text(text)
                summaries.append(f"[PDF资料] {summary}")
        except Exception as e:
            logger.warning(f"analyze_resources: failed to process PDF {pdf_url}: {e}")

    # 处理图片
    for img_url in image_urls[:3]:
        try:
            from langchain_core.messages import HumanMessage as HM
            vision = get_vision_model()
            msg = HM(content=[
                {"type": "text", "text": "请描述这张图片中与备考相关的信息（考试大纲、笔记、教材目录等）。"},
                {"type": "image_url", "image_url": {"url": img_url}},
            ])
            response = await vision.ainvoke([msg])
            content = response.content if isinstance(response.content, str) else str(response.content[0])
            summaries.append(f"[图片资料] {content}")
        except Exception as e:
            logger.warning(f"analyze_resources: failed to process image {img_url}: {e}")

    return {"resource_summary": "\n\n".join(summaries)}


async def check_fields_node(state: Dict) -> Dict:
    """检查必填字段是否齐全，决定是否需要追问（LLM 节点）"""
    try:
        # 追问已达上限，强制不再追问
        if state.get("clarification_rounds", 0) >= 6:
            return {
                "needs_clarification": False,
                "clarification_question": None,
            }

        prompt = CHECK_FIELDS_PROMPT.format(
            exam_name=state.get("exam_name") or "未填写",
            exam_type=state.get("exam_type") or "未填写",
            exam_date=state.get("exam_date") or "未填写",
            daily_hours=state.get("daily_hours") or "未填写",
            foundation_level_desc=get_foundation_level_desc(state.get("foundation_level")),
            weak_subjects=", ".join(state.get("weak_subjects", [])) or "未填写",
            rest_days_per_week=state.get("rest_days_per_week", 1),
            resource_summary=state.get("resource_summary", "（无资料）"),
            clarification_rounds=state.get("clarification_rounds", 0),
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        data = _extract_json(response.content if isinstance(response.content, str) else str(response.content))

        return {
            "needs_clarification": bool(data.get("needs_clarification", False)),
            "clarification_question": data.get("question") if data.get("needs_clarification") else None,
        }
    except Exception as e:
        logger.error(f"check_fields_node error: {e}")
        # 出错时默认不再追问，直接继续流程
        return {"needs_clarification": False, "clarification_question": None}


async def ask_user_node(state: Dict) -> Dict:
    """向用户追问缺失信息（interrupt 节点）"""
    question = state.get("clarification_question", "请补充更多信息")
    rounds = state.get("clarification_rounds", 0) + 1
    return {
        "clarification_question": question,
        "message": question,
        "clarification_rounds": rounds,
    }


async def parse_reply_node(state: Dict) -> Dict:
    """从用户追问回复中提取信息，合并到 state（LLM 节点）"""
    try:
        messages = state.get("messages", [])
        last_human = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)),
            "",
        )

        prompt = PARSE_REPLY_PROMPT.format(
            exam_name=state.get("exam_name") or "未填写",
            exam_type=state.get("exam_type") or "未填写",
            exam_date=state.get("exam_date") or "未填写",
            daily_hours=state.get("daily_hours") or "未填写",
            foundation_level=state.get("foundation_level") or "未填写",
            weak_subjects=", ".join(state.get("weak_subjects", [])) or "未填写",
            question=state.get("clarification_question", ""),
            reply=last_human,
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        data = _extract_json(response.content if isinstance(response.content, str) else str(response.content))

        updates: Dict = {}
        # 只合并非 null 的新值，不覆盖已有值（除非已有值为 None）
        for field in ("exam_name", "exam_type", "exam_date", "daily_hours",
                      "foundation_level", "rest_days_per_week"):
            new_val = data.get(field)
            if new_val is not None:
                old_val = state.get(field)
                if old_val is None:
                    updates[field] = new_val

        # weak_subjects：新值非空时合并
        new_weak = data.get("weak_subjects")
        if new_weak and isinstance(new_weak, list):
            old_weak = state.get("weak_subjects", [])
            merged = list(set(old_weak + new_weak))
            updates["weak_subjects"] = merged

        # 重置追问状态
        updates["clarification_question"] = None

        return updates
    except Exception as e:
        logger.error(f"parse_reply_node error: {e}")
        return {"error": str(e), "clarification_question": None}


async def search_exam_info_node(state: Dict) -> Dict:
    """调用搜索工具获取考试相关信息（工具节点）"""
    try:
        result = await search_exam_info.ainvoke({
            "exam_name": state.get("exam_name", ""),
            "exam_type": state.get("exam_type", ""),
        })
        return {"exam_info": result}
    except Exception as e:
        logger.error(f"search_exam_info_node error: {e}")
        return {"exam_info": {}, "error": str(e)}


async def generate_plan_node(state: Dict) -> Dict:
    """调用 LLM 生成每日学习任务清单（LLM 节点）"""
    try:
        phases_desc = "\n".join(
            f"- {p['phase_name']}：{p['start_date']} ~ {p['end_date']}（{p['days']}天）"
            for p in state.get("phases", [])
        ) or "暂无阶段信息"

        total_plan_days = state.get("total_days", 0)

        prompt = GENERATE_PLAN_PROMPT.format(
            exam_name=state.get("exam_name", ""),
            exam_type=state.get("exam_type", ""),
            exam_date=state.get("exam_date", ""),
            start_date=state.get("phases", [{}])[0].get("start_date", str(date.today())),
            estimated_completion_date=state.get("estimated_completion_date", state.get("exam_date", "")),
            daily_hours=state.get("daily_hours", 2.0),
            foundation_level_desc=get_foundation_level_desc(state.get("foundation_level")),
            weak_subjects=", ".join(state.get("weak_subjects", [])) or "无",
            rest_days_per_week=state.get("rest_days_per_week", 1),
            phases_desc=phases_desc,
            exam_info=json.dumps(state.get("exam_info", {}), ensure_ascii=False),
            resource_summary=state.get("resource_summary", "（无资料）"),
            total_plan_days=total_plan_days,
        )

        llm = get_chat_model()
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        text = response.content if isinstance(response.content, str) else str(response.content)
        tasks = _extract_json(text)

        # 如果返回的是 {"tasks": [...]} 格式，提取 tasks 数组
        if isinstance(tasks, dict) and "tasks" in tasks:
            tasks = tasks["tasks"]

        return {"tasks": tasks}
    except Exception as e:
        logger.error(f"generate_plan_node error: {e}")
        return {"tasks": [], "error": str(e)}


async def save_plan_node(state: Dict) -> Dict:
    """将生成的备考计划保存到数据库（工具节点）"""
    try:
        result = await create_study_plan.ainvoke({
            "user_id": state.get("user_id", ""),
            "exam_name": state.get("exam_name", ""),
            "exam_type": state.get("exam_type", ""),
            "exam_date": state.get("exam_date", ""),
            "daily_hours": state.get("daily_hours", 2.0),
            "tasks": state.get("tasks", []),
        })

        plan_id = result.get("plan_id") or ""
        total_tasks = len(state.get("tasks", []))

        return {
            "plan_id": plan_id,
            "message": f"备考计划已生成！共 {total_tasks} 个学习任务，祝你考试顺利！",
        }
    except Exception as e:
        logger.error(f"save_plan_node error: {e}")
        return {"plan_id": None, "message": "计划保存失败，请稍后重试。", "error": str(e)}
