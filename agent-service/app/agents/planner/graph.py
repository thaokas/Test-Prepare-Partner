"""Planner Agent 工作流图 — 多轮对话式备考计划生成"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.planner.state import PlannerState
from app.agents.planner.nodes import (
    parse_input_node,
    analyze_resources_node,
    check_fields_node,
    ask_user_node,
    parse_reply_node,
    search_exam_info_node,
    calculate_study_time_node,
    generate_plan_node,
    save_plan_node,
)


def _route_after_check_fields(state: PlannerState) -> str:
    """check_fields_node 的条件路由：需要追问 → ask_user，字段齐全 → search_exam_info"""
    if state.get("needs_clarification", False):
        return "ask_user"
    return "search_exam_info"


_builder = StateGraph(PlannerState)

# 添加节点
_builder.add_node("parse_input", parse_input_node)
_builder.add_node("analyze_resources", analyze_resources_node)
_builder.add_node("check_fields", check_fields_node)
_builder.add_node("ask_user", ask_user_node)
_builder.add_node("parse_reply", parse_reply_node)
_builder.add_node("search_exam_info", search_exam_info_node)
_builder.add_node("calculate_study_time", calculate_study_time_node)
_builder.add_node("generate_plan", generate_plan_node)
_builder.add_node("save_plan", save_plan_node)

# 设置入口
_builder.set_entry_point("parse_input")

# 顺序边
_builder.add_edge("parse_input", "analyze_resources")
_builder.add_edge("analyze_resources", "check_fields")

# 条件边：check_fields → ask_user 或 search_exam_info
_builder.add_conditional_edges(
    "check_fields",
    _route_after_check_fields,
    {"ask_user": "ask_user", "search_exam_info": "search_exam_info"},
)

# 追问循环：ask_user → END（interrupt，等待用户回复后从 parse_reply 继续）
_builder.add_edge("ask_user", END)

# 用户回复后：parse_reply → check_fields（循环检查）
_builder.add_edge("parse_reply", "check_fields")

# 完成流程
_builder.add_edge("search_exam_info", "calculate_study_time")
_builder.add_edge("calculate_study_time", "generate_plan")
_builder.add_edge("generate_plan", "save_plan")
_builder.add_edge("save_plan", END)

# 编译图（使用 MemorySaver 支持跨请求多轮对话）
checkpointer = MemorySaver()
planner_graph = _builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["ask_user"],  # 在 ask_user 前暂停，等待用户回复
)