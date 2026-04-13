"""
网络搜索工具 - 供计划生成Agent使用
"""
from typing import Dict, List

from langchain.tools import tool


@tool
async def search_exam_info(exam_name: str, exam_type: str) -> Dict:
    """搜索考试相关信息（科目、时间、备考建议等）

    Args:
        exam_name: 考试名称，如"考研"、"雅思"、"CPA"
        exam_type: 考试科目/方向，如"计算机"、"英语"

    Returns:
        包含考试科目、时间安排、备考建议的字典
    """
    # TODO: 接入 Tavily / SerpAPI 等搜索服务
    return {
        "exam_name": exam_name,
        "exam_type": exam_type,
        "subjects": [],
        "key_dates": {},
        "preparation_tips": f"针对{exam_name}({exam_type})的备考建议",
        "reference_books": []
    }


@tool
async def search_study_resources(subject: str, phase: int) -> List[Dict]:
    """搜索指定学科和备考阶段的学习资源推荐

    Args:
        subject: 学科名称，如"高等数学"、"英语词汇"
        phase: 备考阶段（1-基础 2-强化 3-冲刺）

    Returns:
        推荐资源列表（教材、网课、题库等）
    """
    # TODO: 接入搜索服务
    phase_names = {1: "基础", 2: "强化", 3: "冲刺"}
    return [
        {
            "title": f"{subject}{phase_names.get(phase, '')}阶段学习资源",
            "type": "教材",
            "url": None,
            "description": f"适合{phase_names.get(phase, '')}阶段的{subject}学习材料"
        }
    ]


@tool
async def search_exam_schedule(exam_name: str) -> Dict:
    """搜索考试时间安排（报名、考试、出分日期等）

    Args:
        exam_name: 考试名称

    Returns:
        包含关键时间节点的字典
    """
    # TODO: 接入搜索服务
    return {
        "exam_name": exam_name,
        "registration_deadline": None,
        "exam_date": None,
        "result_date": None,
        "notes": f"请查阅{exam_name}官方网站获取最新时间安排"
    }


SEARCH_TOOLS = [
    search_exam_info,
    search_study_resources,
    search_exam_schedule,
]
