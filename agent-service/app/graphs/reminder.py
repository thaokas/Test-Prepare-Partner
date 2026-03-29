"""
提醒工作流 (LangGraph)

触发条件：定时任务触发（根据用户设置的模式）

模式配置：
| 模式 | 触发时间 | 频率 |
|------|----------|------|
| 温柔 | 22:00 | 每日1次 |
| 强化 | 21:00, 22:00 | 每日2次 |
| 唐僧 | 21:00起每30分钟 | 高频 |
| 静默 | 不触发 | 无 |
"""
from typing import TypedDict, List, Optional
from datetime import datetime


class ReminderState(TypedDict):
    """提醒工作流状态"""
    user_id: str
    mode: int  # 0-静默 1-温柔 2-强化 3-唐僧

    # 未完成任务
    incomplete_tasks: List[dict]
    remaining_count: int

    # 提醒内容
    reminder_type: int  # 1-每日提醒 2-催更提醒 3-周报提醒
    content: str

    # 错误
    error: Optional[str]


# 提醒话术库
REMINDER_TEMPLATES = {
    "gentle": [
        "🌙 今日任务还剩{remaining}项未完成哦，睡前看一眼，明天会更轻松～小搭陪你。",
        "任务没完成没关系，我们慢慢来。你看，小搭已经帮你把计划调温柔了一点～",
        "今天辛苦啦！还有{remaining}个小任务没做完，明天继续加油哦～"
    ],
    "intensive": [
        "⚡ 你知道吗？在你犹豫的这3分钟里，你的竞争对手已经做完了一套题。小搭相信你也不甘落后！",
        "还有{remaining}项任务等待中，现在开始还来得及！",
        "时间在流逝，但小搭会一直陪着你。来，一起把剩下的{remaining}个任务搞定！"
    ],
    "monking": [
        "📿 施主，明日复明日，明日何其多。我生待明日，万事成蹉跎。不如现在翻开书本，可好？小搭陪你。",
        "小搭知道你累，但再坚持一下下嘛......我陪你一起！你看，就差一点点啦～",
        "阿弥陀佛，{remaining}项任务还在等待施主。放下手机，立地学习！",
        "施主，小搭数到三，如果你还不开始，我就跳到你肩膀上监督你——一、二......"
    ]
}


def get_incomplete_tasks_node(state: ReminderState) -> dict:
    """获取未完成任务节点

    TODO: 从数据库查询用户今日未完成任务
    """
    return {
        "incomplete_tasks": [],
        "remaining_count": 0
    }


def select_template_node(state: ReminderState) -> dict:
    """选择提醒模板节点"""
    import random

    mode = state["mode"]
    remaining = state["remaining_count"]

    # 根据模式选择话术库
    if mode == 1:  # 温柔
        templates = REMINDER_TEMPLATES["gentle"]
    elif mode == 2:  # 强化
        templates = REMINDER_TEMPLATES["intensive"]
    elif mode == 3:  # 唐僧
        templates = REMINDER_TEMPLATES["monking"]
    else:  # 静默
        return {"content": ""}

    # 随机选择一个模板
    template = random.choice(templates)
    content = template.format(remaining=remaining)

    return {"content": content}


def create_reminder_graph():
    """创建提醒工作流图"""
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(ReminderState)

    # 添加节点
    workflow.add_node("get_incomplete_tasks", get_incomplete_tasks_node)
    workflow.add_node("select_template", select_template_node)

    # 设置入口
    workflow.set_entry_point("get_incomplete_tasks")

    # 添加边
    workflow.add_edge("get_incomplete_tasks", "select_template")
    workflow.add_edge("select_template", END)

    return workflow.compile()


# 导出编译后的图
reminder_graph = create_reminder_graph()