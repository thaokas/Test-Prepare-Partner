"""Planner Agent 节点函数"""
import json
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

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
