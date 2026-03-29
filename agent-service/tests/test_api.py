"""
API接口测试
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    """测试健康检查"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_not_found():
    """测试聊天接口 - 用户不存在"""
    response = client.post(
        "/api/chat",
        json={
            "user_id": "non_existent_user",
            "message": "你好"
        }
    )
    # 由于用户不存在，应该返回404
    assert response.status_code == 404


def test_plan_generate_not_found():
    """测试计划生成 - 用户不存在"""
    response = client.post(
        "/api/plan/generate",
        json={
            "user_id": "non_existent_user",
            "exam_name": "考研数学",
            "exam_type": "考研",
            "exam_date": "2026-12-21",
            "daily_hours": 4.0,
            "foundation_level": 1,
            "weak_subjects": ["高等数学"]
        }
    )
    # 由于用户不存在，应该返回404
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])