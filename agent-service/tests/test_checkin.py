"""
打卡工作流测试
"""
import pytest
from datetime import datetime

from app.graphs.checkin import checkin_graph, CheckinState


def test_checkin_graph():
    """测试打卡处理工作流"""
    initial_state: CheckinState = {
        "user_id": "test_user_001",
        "content": "打卡",
        "checkin_type": 1,  # 文字打卡

        # 解析结果
        "parsed_tasks": [],
        "matched_task_ids": [],
        "completed_count": 0,
        "total_count": 0,

        # 完成率
        "completion_rate": 0.0,

        # 连续打卡
        "current_streak": 0,
        "streak_updated": False,

        # 彩蛋
        "easter_egg": None,

        # 鼓励话术
        "encouragement": "",

        # 错误
        "error": None
    }

    result = checkin_graph.invoke(initial_state)

    # 验证工作流执行完成
    assert "encouragement" in result
    assert result["encouragement"] != ""


def test_encouragement_generation():
    """测试鼓励话术生成"""
    from app.graphs.checkin import generate_encouragement_node

    # 测试不同完成率
    test_cases = [
        (10.0, "第一步"),
        (25.0, "四分之一"),
        (50.0, "半程"),
        (75.0, "冲刺"),
        (100.0, "恭喜")
    ]

    for rate, expected_keyword in test_cases:
        state = {"completion_rate": rate}
        result = generate_encouragement_node(state)
        assert expected_keyword in result["encouragement"] or "加油" in result["encouragement"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])