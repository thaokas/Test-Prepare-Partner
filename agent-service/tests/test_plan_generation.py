"""
计划生成工作流测试
"""
import pytest
from datetime import date, timedelta

from app.graphs.plan_generation import plan_generation_graph, PlanGenerationState


def test_plan_generation_graph():
    """测试计划生成工作流"""
    # 准备测试数据
    initial_state: PlanGenerationState = {
        "user_id": "test_user_001",
        "exam_name": "考研数学",
        "exam_type": "考研",
        "exam_date": date.today() + timedelta(days=100),  # 100天后考试
        "daily_hours": 4.0,
        "foundation_level": 1,
        "weak_subjects": ["高等数学"],

        # 计算结果（初始为空）
        "days_remaining": 0,
        "current_phase": 0,
        "phase_name": "",

        # 生成的任务
        "tasks": [],

        # 结果
        "plan_id": None,
        "message": None,
        "error": None
    }

    # 执行工作流
    result = plan_generation_graph.invoke(initial_state)

    # 验证结果
    assert result["days_remaining"] == 100
    assert result["current_phase"] == 1  # 基础阶段
    assert result["phase_name"] == "基础阶段"
    assert len(result["tasks"]) > 0


def test_phase_calculation():
    """测试阶段计算逻辑"""
    from app.graphs.plan_generation import calculate_phase_node

    # 测试基础阶段 (>90天)
    state = {"exam_date": date.today() + timedelta(days=100)}
    result = calculate_phase_node(state)
    assert result["current_phase"] == 1

    # 测试强化阶段 (45-90天)
    state = {"exam_date": date.today() + timedelta(days=60)}
    result = calculate_phase_node(state)
    assert result["current_phase"] == 2

    # 测试冲刺阶段 (<45天)
    state = {"exam_date": date.today() + timedelta(days=30)}
    result = calculate_phase_node(state)
    assert result["current_phase"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])