"""计划生成Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.plan_generation.state import PlanGenerationState
from app.agents.plan_generation.nodes import (
    calculate_phase_node,
    search_exam_info_node,
    generate_tasks_node,
    save_plan_node,
)

# 构建工作流图
_builder = StateGraph(PlanGenerationState)

_builder.add_node("calculate_phase", calculate_phase_node)
_builder.add_node("search_exam_info", search_exam_info_node)
_builder.add_node("generate_tasks", generate_tasks_node)
_builder.add_node("save_plan", save_plan_node)

_builder.set_entry_point("calculate_phase")
_builder.add_edge("calculate_phase", "search_exam_info")
_builder.add_edge("search_exam_info", "generate_tasks")
_builder.add_edge("generate_tasks", "save_plan")
_builder.add_edge("save_plan", END)

plan_generation_graph = _builder.compile()
