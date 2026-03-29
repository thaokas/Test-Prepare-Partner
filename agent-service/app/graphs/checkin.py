"""
打卡处理工作流 (LangGraph)

状态节点：
START → parse_content → identify_tasks → mark_complete → calculate_rate → update_streak → check_easter_egg → generate_encouragement → END
"""
from typing import TypedDict, List, Optional
from datetime import date, timedelta


class CheckinState(TypedDict):
    """打卡工作流状态"""
    user_id: str
    content: str
    checkin_type: int  # 1-文字 2-图片

    # 解析结果
    parsed_tasks: List[str]  # 解析出的任务关键词

    # 匹配的任务
    matched_task_ids: List[str]
    completed_count: int
    total_count: int

    # 完成率
    completion_rate: float

    # 连续打卡
    current_streak: int
    streak_updated: bool

    # 彩蛋
    easter_egg: Optional[str]

    # 鼓励话术
    encouragement: str

    # 错误
    error: Optional[str]


# 鼓励话术库
ENCOURAGEMENT_TEMPLATES = {
    10: {
        "text": "迈出第一步就是胜利！今天你已经打败了50%的拖延症患者～小搭会一直陪着你！",
        "action": "竖起小短手比个'1'"
    },
    25: {
        "text": "四分之一里程碑达成！小搭从书包里探出头给你加油～",
        "action": "从书包探出头"
    },
    50: {
        "text": "半程庆祝！小搭为你转圈圈～继续加油！",
        "action": "转圈圈"
    },
    75: {
        "text": "冲刺阶段！小搭握拳为你加油，就差一点点啦！",
        "action": "握拳加油"
    },
    100: {
        "text": "🏆 恭喜完成今日所有任务！小搭从书包里掏出一颗糖送给你～可以安心喝杯奶茶，明天继续冲！",
        "action": "掏糖果动作"
    }
}


def parse_content_node(state: CheckinState) -> dict:
    """解析打卡内容节点

    TODO: 使用LLM解析用户输入，提取任务关键词
    """
    content = state["content"]

    # 简单关键词匹配（TODO: 替换为LLM解析）
    keywords = []
    if "完成" in content or "打卡" in content:
        keywords.append("all")  # 标记全部完成

    return {"parsed_tasks": keywords}


def identify_tasks_node(state: CheckinState) -> dict:
    """识别任务节点

    根据解析结果匹配今日任务
    TODO: 实现数据库查询和任务匹配
    """
    # 占位返回
    return {
        "matched_task_ids": [],
        "completed_count": 0,
        "total_count": 0
    }


def calculate_rate_node(state: CheckinState) -> dict:
    """计算完成率节点"""
    total = state["total_count"]
    completed = state["completed_count"]

    rate = (completed / total * 100) if total > 0 else 0

    return {"completion_rate": round(rate, 2)}


def update_streak_node(state: CheckinState) -> dict:
    """更新连续打卡节点

    TODO: 检查昨天是否打卡，更新streak
    """
    return {
        "streak_updated": True,
        "current_streak": state.get("current_streak", 0) + 1
    }


def check_easter_egg_node(state: CheckinState) -> dict:
    """检查彩蛋触发条件节点

    彩蛋类型：
    - late_night: 深夜打卡
    - early_bird: 早起打卡
    - weekend: 周末打卡
    - random: 随机触发
    """
    from datetime import datetime

    now = datetime.now()
    hour = now.hour

    easter_egg = None

    # 深夜彩蛋 (23:00-5:00)
    if hour >= 23 or hour < 5:
        easter_egg = "🌙 深夜党彩蛋：这么晚还在努力，小搭心疼又佩服！记得早点休息哦～"

    # 早起彩蛋 (5:00-7:00)
    elif 5 <= hour < 7:
        easter_egg = "🌅 早起鸟彩蛋：早安！早起的鸟儿有虫吃，今天一定效率满满！"

    return {"easter_egg": easter_egg}


def generate_encouragement_node(state: CheckinState) -> dict:
    """生成鼓励话术节点"""
    rate = state["completion_rate"]

    # 确定档位
    if rate >= 100:
        tier = 100
    elif rate >= 75:
        tier = 75
    elif rate >= 50:
        tier = 50
    elif rate >= 25:
        tier = 25
    else:
        tier = 10

    template = ENCOURAGEMENT_TEMPLATES[tier]
    encouragement = f"{template['text']} {template['action']}"

    return {"encouragement": encouragement}


def create_checkin_graph():
    """创建打卡处理工作流图"""
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(CheckinState)

    # 添加节点
    workflow.add_node("parse_content", parse_content_node)
    workflow.add_node("identify_tasks", identify_tasks_node)
    workflow.add_node("calculate_rate", calculate_rate_node)
    workflow.add_node("update_streak", update_streak_node)
    workflow.add_node("check_easter_egg", check_easter_egg_node)
    workflow.add_node("generate_encouragement", generate_encouragement_node)

    # 设置入口
    workflow.set_entry_point("parse_content")

    # 添加边
    workflow.add_edge("parse_content", "identify_tasks")
    workflow.add_edge("identify_tasks", "calculate_rate")
    workflow.add_edge("calculate_rate", "update_streak")
    workflow.add_edge("update_streak", "check_easter_egg")
    workflow.add_edge("check_easter_egg", "generate_encouragement")
    workflow.add_edge("generate_encouragement", END)

    return workflow.compile()


# 导出编译后的图
checkin_graph = create_checkin_graph()