"""周报生成Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.report.state import ReportState
from app.agents.report.nodes import (
    calculate_metrics_node,
    analyze_performance_node,
    generate_html_report_node,
    save_report_node,
)

_builder = StateGraph(ReportState)

_builder.add_node("calculate_metrics", calculate_metrics_node)
_builder.add_node("analyze_performance", analyze_performance_node)
_builder.add_node("generate_html_report", generate_html_report_node)
_builder.add_node("save_report", save_report_node)

_builder.set_entry_point("calculate_metrics")
_builder.add_edge("calculate_metrics", "analyze_performance")
_builder.add_edge("analyze_performance", "generate_html_report")
_builder.add_edge("generate_html_report", "save_report")
_builder.add_edge("save_report", END)

report_graph = _builder.compile()
