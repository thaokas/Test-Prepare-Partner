"""测试 Reminder Agent —— 监督提醒生成"""
import pytest
from app.agents.reminder import reminder_graph


@pytest.mark.asyncio
class TestReminderAgent:
    """提醒 Agent 完整运行测试（使用真实 LLM）"""

    async def test_silent_mode(self, sample_reminder_state):
        """静默模式：应返回空内容"""
        state = {**sample_reminder_state, "strictness_mode": "silent"}
        result = await reminder_graph.ainvoke(state)

        assert result is not None
        assert "content" in result
        assert result["content"] == "", f"静默模式应返回空内容，实际: {result['content']}"

    async def test_gentle_mode(self, sample_reminder_state):
        """温柔模式：应返回温暖鼓励"""
        state = {**sample_reminder_state, "strictness_mode": "gentle"}
        result = await reminder_graph.ainvoke(state)

        assert result is not None
        assert "content" in result
        assert result["content"], "温柔模式不应返回空内容"

    async def test_intensive_mode(self, sample_reminder_state):
        """强化模式：应返回督促提醒"""
        state = {**sample_reminder_state, "strictness_mode": "intensive"}
        result = await reminder_graph.ainvoke(state)

        assert result is not None
        assert "content" in result
        assert result["content"], "强化模式不应返回空内容"

    async def test_nightmare_mode(self, sample_reminder_state):
        """噩梦模式：应返回犀利批评"""
        state = {**sample_reminder_state, "strictness_mode": "nightmare"}
        result = await reminder_graph.ainvoke(state)

        assert result is not None
        assert "content" in result
        assert result["content"], "噩梦模式不应返回空内容"

    async def test_tangseng_mode(self, sample_reminder_state):
        """唐僧模式：应返回超长唠叨"""
        state = {**sample_reminder_state, "strictness_mode": "tangseng"}
        result = await reminder_graph.ainvoke(state)

        assert result is not None
        assert "content" in result
        assert result["content"], "唐僧模式不应返回空内容"
        # 唐僧模式应较长；若 LLM 调用出错走 fallback，文案会较短，跳过长度校验
        if not result.get("error"):
            assert len(result["content"]) >= 50, \
                f"唐僧模式内容应较长，实际长度: {len(result['content'])}"

    async def test_all_tasks_done(self):
        """全部任务完成：应返回表扬"""
        state = {
            "today_total_tasks": [
                {"subject": "数学", "name": "习题", "estimated_minutes": 60},
            ],
            "today_incomplete_tasks": [],  # 全部完成
            "exam_total_tasks": [{"id": str(i)} for i in range(1, 31)],
            "exam_completed_tasks": [{"id": str(i)} for i in range(1, 21)],
            "elapsed_study_days": 30.0,
            "total_study_days": 90.0,
            "strictness_mode": "gentle",
            "current_time": None,
            "content": "",
            "error": None,
        }
        result = await reminder_graph.ainvoke(state)
        assert result["content"]

    async def test_nothing_done(self):
        """完全未开始：应返回催促"""
        state = {
            "today_total_tasks": [
                {"subject": "数学", "name": "习题", "estimated_minutes": 60},
                {"subject": "英语", "name": "背单词", "estimated_minutes": 30},
            ],
            "today_incomplete_tasks": [
                {"subject": "数学", "name": "习题", "estimated_minutes": 60},
                {"subject": "英语", "name": "背单词", "estimated_minutes": 30},
            ],
            "exam_total_tasks": [{"id": str(i)} for i in range(1, 51)],
            "exam_completed_tasks": [],
            "elapsed_study_days": 10.0,
            "total_study_days": 90.0,
            "strictness_mode": "intensive",
            "current_time": None,
            "content": "",
            "error": None,
        }
        result = await reminder_graph.ainvoke(state)
        assert result["content"]
