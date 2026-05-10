"""测试 Planner Agent —— 备考计划生成（无状态 API）"""
import pytest
from datetime import date, timedelta

from app.agents.planner import get_planner_agent
from app.agents.planner.state import ExamProfile, PlannerState


def _profile_to_dict(state: PlannerState) -> dict:
    """Convert PlannerState.profile to the dict format used by the API."""
    p = state.profile
    return {
        "exam_name": p.exam_name,
        "exam_type": p.exam_type,
        "exam_date": p.exam_date,
        "daily_hours": p.daily_hours,
        "foundation_level": p.foundation_level,
        "weak_subjects": p.weak_subjects,
        "rest_days_per_week": p.rest_days_per_week,
    }


@pytest.mark.asyncio
class TestPlannerAgent:
    """计划生成 Agent 完整运行测试（使用真实 LLM）"""

    async def test_one_shot_generation(self, sample_planner_state):
        """一次性计划生成：信息齐全，直接生成"""
        agent = get_planner_agent()
        profile_dict = _profile_to_dict(sample_planner_state)

        result = await agent.chat(
            user_id=sample_planner_state.user_id,
            message="帮我制定一个考研数学一的备考计划",
            profile=profile_dict,
        )

        assert result is not None
        assert result["status"] in ("completed", "waiting_for_input", "error")

        if result["status"] == "completed":
            assert "tasks" in result
            assert isinstance(result["tasks"], list)
            if result["tasks"]:
                task = result["tasks"][0]
                assert "task_date" in task
                assert "subject" in task
                assert "task_content" in task

    async def test_multi_turn_clarification(self):
        """多轮追问：信息不全时应返回 waiting_for_input"""
        agent = get_planner_agent()

        result = await agent.chat(
            user_id="test-user-002",
            message="帮我制定一个备考计划",
        )

        assert result is not None
        assert result["status"] in ("waiting_for_input", "error")
        if result["status"] == "waiting_for_input":
            assert result["message"], "应返回追问消息"

    async def test_plan_with_short_timeline(self):
        """短期备考：剩余 20 天"""
        agent = get_planner_agent()
        exam_date = (date.today() + timedelta(days=20)).strftime("%Y-%m-%d")
        profile = {
            "exam_name": "期末考试",
            "exam_type": "期末",
            "exam_date": exam_date,
            "daily_hours": 4.0,
            "foundation_level": 1,
            "weak_subjects": [],
            "rest_days_per_week": 1,
        }

        result = await agent.chat(
            user_id="test-short",
            message=f"我要准备期末考试，{exam_date}考试，每天能学4小时，有一定基础",
            profile=profile,
        )

        assert result is not None
        assert result["status"] in ("completed", "waiting_for_input", "error")

        # Verify profile is returned correctly
        assert result.get("profile") is not None

    async def test_plan_with_long_timeline(self):
        """长期备考：剩余 200 天"""
        agent = get_planner_agent()
        exam_date = (date.today() + timedelta(days=200)).strftime("%Y-%m-%d")
        profile = {
            "exam_name": "考研数学一",
            "exam_type": "考研",
            "exam_date": exam_date,
            "daily_hours": 3.0,
            "foundation_level": 0,
            "weak_subjects": ["线性代数"],
            "rest_days_per_week": 1,
        }

        result = await agent.chat(
            user_id="test-long",
            message=f"我想备考考研数学一，{exam_date}考试，每天3小时，零基础，线性代数比较薄弱",
            profile=profile,
        )

        assert result is not None
        assert result["status"] in ("completed", "waiting_for_input", "error")

        # Verify profile is returned
        assert result.get("profile") is not None


class TestExamProfile:
    """ExamProfile 单元测试（无需 LLM）"""

    def test_is_ready_all_filled(self):
        """所有必填字段有值 → is_ready = True"""
        profile = ExamProfile(
            exam_name="雅思",
            exam_date="2026-12-01",
            daily_hours=3.0,
            foundation_level=1,
        )
        assert profile.is_ready is True

    def test_is_ready_missing_fields(self):
        """缺少必填字段 → is_ready = False"""
        profile = ExamProfile(exam_name="雅思")
        assert profile.is_ready is False

    def test_missing_fields_names(self):
        """missing_fields 返回正确的字段名"""
        profile = ExamProfile(exam_name="雅思")
        missing = profile.missing_fields
        assert "考试日期" in missing
        assert "每天学习时间" in missing
        assert "基础水平" in missing
        assert "考试名称" not in missing

    def test_foundation_level_zero_is_valid(self):
        """foundation_level=0 是有效值"""
        profile = ExamProfile(
            exam_name="雅思",
            exam_date="2026-12-01",
            daily_hours=3.0,
            foundation_level=0,
        )
        assert profile.is_ready is True
        assert profile.missing_fields == []

    def test_summary_formatting(self):
        """summary() 方法正确格式化"""
        profile = ExamProfile(
            exam_name="雅思",
            exam_type="学术类",
            exam_date="2026-12-01",
            daily_hours=3.0,
            foundation_level=0,
            weak_subjects=["写作", "口语"],
        )
        summary = profile.summary()
        assert "雅思" in summary
        assert "学术类" in summary
        assert "2026-12-01" in summary
        assert "3.0小时" in summary
        assert "零基础" in summary
        assert "写作" in summary


@pytest.mark.slow
@pytest.mark.asyncio
async def test_multi_turn_state_accumulation():
    """多轮对话：验证 profile 在多个对话轮次中正确累积备考信息（无状态 API）"""
    agent = get_planner_agent()

    # ── Turn 1：用户提到考试和部分信息 ──────────────────────────
    result1 = await agent.chat(
        user_id="test-multiturn",
        message="我想备考雅思，2026年12月考试，每天能学3小时",
    )

    profile1 = result1.get("profile", {})
    messages1 = result1.get("messages", [])
    search_results1 = result1.get("search_results", [])

    print(f"Turn 1 profile: {profile1}")

    assert profile1.get("exam_name") is not None, \
        f"Turn 1 应提取 exam_name, 实际: {profile1.get('exam_name')}"
    assert profile1.get("daily_hours") is not None, \
        f"Turn 1 应提取 daily_hours, 实际: {profile1.get('daily_hours')}"

    exam_name_t1 = profile1["exam_name"]
    daily_hours_t1 = profile1["daily_hours"]

    # ── Turn 2：用户补充更多信息 ─────────────────────────────
    result2 = await agent.chat(
        user_id="test-multiturn",
        message="学术类的，我英语基础还可以，但写作比较薄弱",
        profile=profile1,
        search_results=search_results1,
        messages=messages1,
    )

    profile2 = result2.get("profile", {})
    print(f"Turn 2 profile: {profile2}")

    # ★ 关键断言：Turn 1 的信息必须在 Turn 2 中保留 ★
    assert profile2.get("exam_name") == exam_name_t1, \
        f"BUG: exam_name 从 '{exam_name_t1}' 变成了 '{profile2.get('exam_name')}'"
    assert profile2.get("daily_hours") == daily_hours_t1, \
        f"BUG: daily_hours 从 {daily_hours_t1} 变成了 {profile2.get('daily_hours')}"

    # Turn 2 新提取的信息
    assert profile2.get("foundation_level") is not None, \
        f"Turn 2 应提取 foundation_level, 实际: {profile2.get('foundation_level')}"

    print("多轮状态累积验证通过！")
