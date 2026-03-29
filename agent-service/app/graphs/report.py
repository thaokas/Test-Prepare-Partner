"""
周报工作流 (LangGraph)

触发条件：每周日22:00自动触发 / 用户输入"周报"

数据处理：
- 每日完成率列表
- 平均完成率
- 环比变化
- 连续打卡天数
- 最佳学习时段
"""
from typing import TypedDict, List, Optional
from datetime import date, timedelta


class ReportState(TypedDict):
    """周报工作流状态"""
    user_id: str

    # 日期范围
    week_start: str
    week_end: str

    # 原始数据
    daily_checkins: List[dict]

    # 计算结果
    daily_rates: List[dict]
    average_rate: float
    week_over_week: float
    current_streak: int
    best_study_time: Optional[str]

    # 生成的周报
    summary: str

    # 错误
    error: Optional[str]


def aggregate_data_node(state: ReportState) -> dict:
    """聚合周数据节点

    TODO: 从数据库查询本周和上周数据
    """
    return {
        "daily_checkins": []
    }


def calculate_metrics_node(state: ReportState) -> dict:
    """计算指标节点"""
    checkins = state["daily_checkins"]

    if not checkins:
        return {
            "daily_rates": [],
            "average_rate": 0.0,
            "week_over_week": 0.0,
            "best_study_time": None
        }

    # 计算每日完成率
    daily_rates = [
        {"date": c["date"], "rate": c["completion_rate"]}
        for c in checkins
    ]

    # 计算平均完成率
    avg_rate = sum(c["completion_rate"] for c in checkins) / len(checkins)

    # TODO: 计算环比和最佳学习时段

    return {
        "daily_rates": daily_rates,
        "average_rate": round(avg_rate, 2),
        "week_over_week": 0.0,
        "best_study_time": None
    }


def generate_summary_node(state: ReportState) -> dict:
    """生成周报总结节点"""
    avg_rate = state["average_rate"]
    streak = state["current_streak"]

    # 根据平均完成率生成不同风格的总结
    if avg_rate >= 80:
        summary = f"本周表现优秀！平均完成率{avg_rate:.1f}%"
        if streak >= 7:
            summary += f"，连续打卡{streak}天，太棒了！"
        else:
            summary += "，继续保持！"
    elif avg_rate >= 50:
        summary = f"本周表现良好，平均完成率{avg_rate:.1f}%，还有提升空间哦～"
    else:
        summary = f"本周平均完成率{avg_rate:.1f}%，下周加油！小搭陪你一起努力！"

    return {"summary": summary}


def create_report_graph():
    """创建周报工作流图"""
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(ReportState)

    # 添加节点
    workflow.add_node("aggregate_data", aggregate_data_node)
    workflow.add_node("calculate_metrics", calculate_metrics_node)
    workflow.add_node("generate_summary", generate_summary_node)

    # 设置入口
    workflow.set_entry_point("aggregate_data")

    # 添加边
    workflow.add_edge("aggregate_data", "calculate_metrics")
    workflow.add_edge("calculate_metrics", "generate_summary")
    workflow.add_edge("generate_summary", END)

    return workflow.compile()


# 导出编译后的图
report_graph = create_report_graph()