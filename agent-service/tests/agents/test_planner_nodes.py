"""Planner Agent 节点单元测试"""
import json
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import date, timedelta


# ── calculate_study_time_node ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_calculate_study_time_120_days():
    """120天备考：应生成基础+强化+冲刺三阶段。"""
    from app.agents.planner.nodes import calculate_study_time_node

    fixed_today = date(2026, 4, 14)
    exam_date_str = str(fixed_today + timedelta(days=120))

    state = {
        "exam_date": exam_date_str,
        "daily_hours": 2.0,
        "rest_days_per_week": 1,
    }

    with patch("app.agents.planner.nodes.date") as mock_date:
        mock_date.today.return_value = fixed_today
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = await calculate_study_time_node(state)

    assert result["total_days"] == 120
    assert len(result["phases"]) == 3
    phase_nums = [p["phase"] for p in result["phases"]]
    assert phase_nums == [1, 2, 3]
    assert result["phases"][0]["phase_name"] == "基础阶段"
    assert result["phases"][1]["phase_name"] == "强化阶段"
    assert result["phases"][2]["phase_name"] == "冲刺阶段"


@pytest.mark.asyncio
async def test_calculate_study_time_50_days():
    """50天备考：仅有强化+冲刺两阶段（无基础阶段）。"""
    from app.agents.planner.nodes import calculate_study_time_node

    fixed_today = date(2026, 4, 14)
    exam_date_str = str(fixed_today + timedelta(days=50))

    state = {
        "exam_date": exam_date_str,
        "daily_hours": 2.0,
        "rest_days_per_week": 1,
    }

    with patch("app.agents.planner.nodes.date") as mock_date:
        mock_date.today.return_value = fixed_today
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = await calculate_study_time_node(state)

    assert result["total_days"] == 50
    phase_nums = [p["phase"] for p in result["phases"]]
    assert 1 not in phase_nums
    assert 2 in phase_nums
    assert 3 in phase_nums


@pytest.mark.asyncio
async def test_calculate_study_time_high_daily_hours_finishes_early():
    """每日学习时间很长时，estimated_completion_date 应早于 exam_date。"""
    from app.agents.planner.nodes import calculate_study_time_node

    fixed_today = date(2026, 4, 14)
    exam_date_str = str(fixed_today + timedelta(days=200))

    state = {
        "exam_date": exam_date_str,
        "daily_hours": 8.0,   # 高学习强度
        "rest_days_per_week": 1,
    }

    with patch("app.agents.planner.nodes.date") as mock_date:
        mock_date.today.return_value = fixed_today
        mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
        result = await calculate_study_time_node(state)

    from datetime import datetime
    completion = datetime.strptime(result["estimated_completion_date"], "%Y-%m-%d").date()
    exam = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
    assert completion < exam, "高强度学习应在考试日之前完成备考"
