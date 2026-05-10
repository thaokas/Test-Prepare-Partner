"""
网络搜索工具 — 供计划生成 Agent 使用
使用 DuckDuckGo 搜索，无需 API Key。搜索失败时优雅降级。
"""
import logging
from typing import Dict, List

from langchain.tools import tool

logger = logging.getLogger(__name__)


def _web_search(query: str, max_results: int = 5) -> List[Dict]:
    """执行 DuckDuckGo 网页搜索，返回结果列表。失败时返回空列表。"""
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                })
            if results:
                return results
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed: {e}")

    # 尝试 ddgs 新包名
    try:
        from ddgs import DDGS as DDGS2
        with DDGS2() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "url": r.get("href", ""),
                })
            if results:
                return results
    except Exception as e:
        logger.warning(f"ddgs search also failed: {e}")

    return []


@tool
async def search_exam_info(exam_name: str, exam_type: str = "") -> Dict:
    """搜索考试相关信息（科目、考试时间、备考建议、大纲等）

    Args:
        exam_name: 考试名称，如"考研"、"雅思"、"CPA"、"高考"
        exam_type: 考试科目/方向（可选），如"数学一"、"学术类"

    Returns:
        包含考试相关信息的字典
    """
    query = f"{exam_name} {exam_type} 考试科目 考试时间 备考建议".strip()
    logger.info(f"Searching exam info: {query}")

    results = _web_search(query, max_results=5)

    if not results:
        # 用中文再试一次
        query_cn = f"{exam_name}{exam_type} 考试大纲 备考经验".strip()
        results = _web_search(query_cn, max_results=5)

    if not results:
        return {
            "query": query,
            "error": "未搜索到相关信息，请用户自行提供考试详情",
            "sources": [],
        }

    return {
        "query": query,
        "summary": f"搜索到 {len(results)} 条关于 {exam_name}{exam_type} 的结果",
        "sources": results,
    }


@tool
async def search_study_resources(subject: str, phase: int = 1) -> Dict:
    """搜索指定学科和备考阶段的学习资源推荐

    Args:
        subject: 学科名称，如"高等数学"、"英语词汇"
        phase: 备考阶段（1=基础 2=强化 3=冲刺）

    Returns:
        推荐资源列表
    """
    phase_names = {1: "基础", 2: "强化", 3: "冲刺"}
    phase_cn = phase_names.get(phase, "备考")

    query = f"{subject} {phase_cn}阶段 学习资料 推荐 教材 网课"
    logger.info(f"Searching study resources: {query}")

    results = _web_search(query, max_results=5)

    if not results:
        return {
            "subject": subject,
            "phase": phase,
            "error": "未找到相关资源推荐",
            "sources": [],
        }

    return {
        "subject": subject,
        "phase": phase,
        "phase_name": phase_cn,
        "summary": f"搜索到 {len(results)} 条 {subject} {phase_cn}阶段 学习资源",
        "sources": results,
    }


@tool
async def search_exam_schedule(exam_name: str) -> Dict:
    """搜索考试时间安排（报名时间、考试日期、成绩公布等关键节点）

    Args:
        exam_name: 考试名称

    Returns:
        包含关键时间节点的字典
    """
    current_year = __import__("datetime").datetime.now().year
    query = f"{exam_name} {current_year}年 报名时间 考试时间 成绩查询"

    logger.info(f"Searching exam schedule: {query}")
    results = _web_search(query, max_results=5)

    if not results:
        return {
            "exam_name": exam_name,
            "error": "未搜索到考试时间安排",
            "sources": [],
        }

    return {
        "exam_name": exam_name,
        "summary": f"搜索到 {len(results)} 条关于 {exam_name} 时间安排的结果",
        "sources": results,
    }


SEARCH_TOOLS = [
    search_exam_info,
    search_study_resources,
    search_exam_schedule,
]
