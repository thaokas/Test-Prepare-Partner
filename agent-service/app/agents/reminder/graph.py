"""监督提醒Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.reminder.state import ReminderState
from app.agents.reminder.nodes import get_current_time_node, generate_reminder_node


def _route_after_time(state: ReminderState) -> str:
    """get_current_time_node 完成后的路由：silent 模式直接结束。"""
    if state.get("strictness_mode") == "silent":
        return END
    return "generate_reminder"


_builder = StateGraph(ReminderState)

_builder.add_node("get_current_time", get_current_time_node)
_builder.add_node("generate_reminder", generate_reminder_node)

_builder.set_entry_point("get_current_time")
_builder.add_conditional_edges("get_current_time", _route_after_time)
_builder.add_edge("generate_reminder", END)

reminder_graph = _builder.compile()
