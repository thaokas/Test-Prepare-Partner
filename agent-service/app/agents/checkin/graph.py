"""打卡处理Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.checkin.state import CheckinState
from app.agents.checkin.nodes import (
    parse_content_node,
    identify_tasks_node,
    calculate_rate_node,
    check_streak_node,
    check_easter_egg_node,
    generate_encouragement_node,
    save_checkin_node,
)

_builder = StateGraph(CheckinState)

_builder.add_node("parse_content", parse_content_node)
_builder.add_node("identify_tasks", identify_tasks_node)
_builder.add_node("calculate_rate", calculate_rate_node)
_builder.add_node("check_streak", check_streak_node)
_builder.add_node("check_easter_egg", check_easter_egg_node)
_builder.add_node("generate_encouragement", generate_encouragement_node)
_builder.add_node("save_checkin", save_checkin_node)

_builder.set_entry_point("parse_content")
_builder.add_edge("parse_content", "identify_tasks")
_builder.add_edge("identify_tasks", "calculate_rate")
_builder.add_edge("calculate_rate", "check_streak")
_builder.add_edge("check_streak", "check_easter_egg")
_builder.add_edge("check_easter_egg", "generate_encouragement")
_builder.add_edge("generate_encouragement", "save_checkin")
_builder.add_edge("save_checkin", END)

checkin_graph = _builder.compile()
