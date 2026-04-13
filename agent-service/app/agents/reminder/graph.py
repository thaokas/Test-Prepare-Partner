"""监督提醒Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.reminder.state import ReminderState
from app.agents.reminder.nodes import (
    get_incomplete_tasks_node,
    analyze_user_status_node,
    generate_reminder_node,
)

_builder = StateGraph(ReminderState)

_builder.add_node("get_incomplete_tasks", get_incomplete_tasks_node)
_builder.add_node("analyze_user_status", analyze_user_status_node)
_builder.add_node("generate_reminder", generate_reminder_node)

_builder.set_entry_point("get_incomplete_tasks")
_builder.add_edge("get_incomplete_tasks", "analyze_user_status")
_builder.add_edge("analyze_user_status", "generate_reminder")
_builder.add_edge("generate_reminder", END)

reminder_graph = _builder.compile()
