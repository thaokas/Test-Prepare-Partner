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


# ── parse_input_node ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_input_extracts_exam_info():
    """parse_input_node 应从 LLM 响应中提取考试信息字段。"""
    from app.agents.planner.nodes import parse_input_node
    from langchain_core.messages import HumanMessage, AIMessage

    llm_json = json.dumps({
        "exam_name": "考研数学",
        "exam_type": "考研",
        "exam_date": "2026-12-26",
        "daily_hours": 3.0,
        "foundation_level": 1,
        "weak_subjects": ["高等数学"],
        "rest_days_per_week": 1,
        "urls": [],
        "pdf_urls": [],
        "image_urls": [],
    })

    mock_response = MagicMock()
    mock_response.content = llm_json

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)

    state = {
        "user_id": "u1",
        "messages": [HumanMessage(content="我要备考考研数学，考试在2026年12月26日，每天能学3小时")],
        "urls": [],
        "pdf_urls": [],
        "image_urls": [],
        "resource_summary": "",
        "exam_name": None,
        "exam_type": None,
        "exam_date": None,
        "daily_hours": None,
        "foundation_level": None,
        "weak_subjects": [],
        "rest_days_per_week": 1,
        "clarification_rounds": 0,
        "clarification_question": None,
        "exam_info": {},
        "total_days": 0,
        "phases": [],
        "estimated_completion_date": "",
        "tasks": [],
        "plan_id": None,
        "message": "",
        "error": None,
    }

    with patch("app.agents.planner.nodes.get_chat_model", return_value=mock_llm):
        result = await parse_input_node(state)

    assert result["exam_name"] == "考研数学"
    assert result["exam_type"] == "考研"
    assert result["exam_date"] == "2026-12-26"
    assert result["daily_hours"] == 3.0
    assert result["foundation_level"] == 1
    assert result["weak_subjects"] == ["高等数学"]


@pytest.mark.asyncio
async def test_parse_input_extracts_urls_from_message():
    """parse_input_node 应将 LLM 返回中的 URL 列表写入 state。"""
    from app.agents.planner.nodes import parse_input_node
    from langchain_core.messages import HumanMessage

    llm_json = json.dumps({
        "exam_name": "雅思",
        "exam_type": "语言",
        "exam_date": None,
        "daily_hours": None,
        "foundation_level": None,
        "weak_subjects": [],
        "rest_days_per_week": 1,
        "urls": ["https://example.com/ielts-guide"],
        "pdf_urls": ["https://example.com/vocab.pdf"],
        "image_urls": [],
    })

    mock_response = MagicMock()
    mock_response.content = llm_json
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)

    state = {
        "user_id": "u1",
        "messages": [HumanMessage(content="备考雅思，参考 https://example.com/ielts-guide 和 https://example.com/vocab.pdf")],
        "urls": [],
        "pdf_urls": [],
        "image_urls": [],
        "resource_summary": "",
        "exam_name": None, "exam_type": None, "exam_date": None,
        "daily_hours": None, "foundation_level": None,
        "weak_subjects": [], "rest_days_per_week": 1,
        "clarification_rounds": 0, "clarification_question": None,
        "exam_info": {}, "total_days": 0, "phases": [],
        "estimated_completion_date": "", "tasks": [],
        "plan_id": None, "message": "", "error": None,
    }

    with patch("app.agents.planner.nodes.get_chat_model", return_value=mock_llm):
        result = await parse_input_node(state)

    assert "https://example.com/ielts-guide" in result["urls"]
    assert "https://example.com/vocab.pdf" in result["pdf_urls"]
