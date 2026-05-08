"""打卡处理Agent工作流图"""
from langgraph.graph import StateGraph, END

from app.agents.checkin.state import CheckinState
from app.agents.checkin.nodes import summarize_image_node, generate_encouragement_node


def _route_by_image(state: CheckinState) -> str:
    """有图片时先总结图片，无图片时直接生成鼓励"""
    if state.get("image_url"):
        return "summarize_image"
    return "generate_encouragement"


_builder = StateGraph(CheckinState)

_builder.add_node("summarize_image", summarize_image_node)
_builder.add_node("generate_encouragement", generate_encouragement_node)

_builder.set_conditional_entry_point(
    _route_by_image,
    {
        "summarize_image": "summarize_image",
        "generate_encouragement": "generate_encouragement",
    },
)
_builder.add_edge("summarize_image", "generate_encouragement")
_builder.add_edge("generate_encouragement", END)

checkin_graph = _builder.compile()
