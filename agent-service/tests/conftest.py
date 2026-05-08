"""测试配置 & 共享 fixtures"""
import pytest
from datetime import date, timedelta
from langchain_core.messages import HumanMessage


@pytest.fixture
def sample_checkin_state():
    """打卡测试的初始 state"""
    return {
        "completed_content": "完成了高数第三章不定积分的学习和习题",
        "overall_completion_rate": 45.0,
        "image_url": None,
        "encouragement": "",
        "error": None,
    }


@pytest.fixture
def sample_planner_state():
    """计划生成测试的初始 state（信息齐全，不触发追问）"""
    exam_date = (date.today() + timedelta(days=90)).strftime("%Y-%m-%d")
    return {
        "user_id": "test-user-001",
        "messages": [HumanMessage(content="我要备考考研数学一，零基础")],
        "urls": [],
        "pdf_urls": [],
        "image_urls": [],
        "resource_summary": "",
        "exam_name": "考研数学一",
        "exam_type": "考研",
        "exam_date": exam_date,
        "daily_hours": 3.0,
        "foundation_level": 0,
        "weak_subjects": ["线性代数"],
        "rest_days_per_week": 1,
        "clarification_rounds": 6,  # 跳过追问
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


@pytest.fixture
def sample_reminder_state():
    """提醒测试的初始 state"""
    return {
        "today_total_tasks": [
            {"subject": "数学", "name": "完成第三章习题", "estimated_minutes": 60},
            {"subject": "英语", "name": "背单词50个", "estimated_minutes": 30},
            {"subject": "政治", "name": "复习第二章", "estimated_minutes": 45},
        ],
        "today_incomplete_tasks": [
            {"subject": "数学", "name": "完成第三章习题", "estimated_minutes": 60},
            {"subject": "政治", "name": "复习第二章", "estimated_minutes": 45},
        ],
        "exam_total_tasks": [{"id": str(i)} for i in range(1, 51)],
        "exam_completed_tasks": [{"id": str(i)} for i in range(1, 16)],
        "elapsed_study_days": 30.0,
        "total_study_days": 90.0,
        "strictness_mode": "gentle",
        "current_time": None,
        "content": "",
        "error": None,
    }


@pytest.fixture
def sample_report_state():
    """周报测试的初始 state"""
    week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")
    week_end = (date.today() - timedelta(days=date.today().weekday()) + timedelta(days=6)).strftime("%Y-%m-%d")
    return {
        "user_id": "test-user-001",
        "week_start": week_start,
        "week_end": week_end,
        "total_plan": [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "数学", "estimated_minutes": 60}
            for i in range(5)
        ] + [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "英语", "estimated_minutes": 30}
            for i in range(3)
        ] + [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "政治", "estimated_minutes": 45}
            for i in range(2)
        ],
        "weekly_completed": [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "数学", "estimated_minutes": 60}
            for i in range(4)
        ] + [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "英语", "estimated_minutes": 30}
            for i in range(2)
        ],
        "subject_stats": [],
        "total_planned": 0,
        "total_completed": 0,
        "total_rate": 0.0,
        "estimated_minutes_total": 0,
        "completed_minutes": 0,
        "streak_days": 0,
        "highlights": [],
        "issues": [],
        "html_content": "",
        "summary": "",
        "report_id": None,
        "error": None,
    }
