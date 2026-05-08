"""测试 Checkin Agent —— 打卡鼓励生成"""
import pytest
from app.agents.checkin import checkin_graph


@pytest.mark.asyncio
class TestCheckinAgent:
    """打卡 Agent 完整运行测试（使用真实 LLM）"""

    async def test_text_only_checkin(self, sample_checkin_state):
        """无图片打卡：输入完成内容，应返回鼓励文案"""
        result = await checkin_graph.ainvoke(sample_checkin_state)

        assert result is not None
        assert "encouragement" in result
        assert result["encouragement"], "鼓励文案不应为空"
        assert len(result["encouragement"]) > 0
        assert any("一" <= c <= "鿿" for c in result["encouragement"]), \
            "鼓励文案应包含中文"
        print(result)

    async def test_checkin_with_image(self, sample_checkin_state):
        """带图片打卡：输入图片 URL，应经过图片总结再生成鼓励"""
        state = {
            **sample_checkin_state,
            "image_url": "/tests/images/note1.png",
        }
        result = await checkin_graph.ainvoke(state)
        print(result)

        assert result is not None
        assert "encouragement" in result
        assert result["encouragement"], "鼓励文案不应为空"

    async def test_checkin_high_rate(self):
        """高完成率打卡：测试不同完成率下的鼓励"""
        state = {
            "completed_content": "今天完成了所有计划任务",
            "overall_completion_rate": 90.0,
            "image_url": None,
            "encouragement": "",
            "error": None,
        }
        result = await checkin_graph.ainvoke(state)
        print(result)
        assert result["encouragement"]

    async def test_checkin_low_rate(self):
        """低完成率打卡"""
        state = {
            "completed_content": "今天只复习了一点",
            "overall_completion_rate": 15.0,
            "image_url": None,
            "encouragement": "",
            "error": None,
        }
        result = await checkin_graph.ainvoke(state)
        print(result)
        assert result["encouragement"]

    async def test_checkin_empty_content(self):
        """空内容打卡：边界情况"""
        state = {
            "completed_content": "",
            "overall_completion_rate": 0.0,
            "image_url": None,
            "encouragement": "",
            "error": None,
        }
        result = await checkin_graph.ainvoke(state)
        print(result)
        assert "encouragement" in result
