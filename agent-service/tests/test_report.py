"""测试 Report Agent —— 周报生成"""
import pytest
from datetime import date, timedelta
from app.agents.report import report_graph


@pytest.mark.asyncio
class TestReportAgent:
    """周报 Agent 完整运行测试（使用真实 LLM）"""

    async def test_weekly_report(self, sample_report_state):
        """正常周报生成"""
        result = await report_graph.ainvoke(sample_report_state)

        assert result is not None

        # 纯计算节点 —— 无论 LLM 是否成功都必须产出
        assert "subject_stats" in result
        assert isinstance(result["subject_stats"], list)
        assert "total_rate" in result
        assert isinstance(result["total_rate"], float)
        assert "total_completed" in result
        assert "total_planned" in result
        assert "streak_days" in result

        # LLM 分析节点
        assert "highlights" in result
        assert isinstance(result["highlights"], list)
        assert "issues" in result

        # HTML 周报 —— LLM 成功时有内容
        assert "html_content" in result
        if not result.get("error"):
            assert result["html_content"], "LLM 成功时 HTML 周报不应为空"
            assert "<!DOCTYPE html>" in result["html_content"]
        else:
            # LLM 失败时也应返回空 html_content（不阻塞流程）
            pass

        # 摘要
        assert "summary" in result

    async def test_empty_week(self):
        """空任务周：本周无计划 —— 验证计算节点正确性"""
        week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")
        week_end = (date.today() - timedelta(days=date.today().weekday()) + timedelta(days=6)).strftime("%Y-%m-%d")
        state = {
            "user_id": "test-empty-week",
            "week_start": week_start,
            "week_end": week_end,
            "total_plan": [],
            "weekly_completed": [],
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
        result = await report_graph.ainvoke(state)

        assert result is not None
        # 纯计算节点：空任务时指标应为 0
        assert result["total_rate"] == 0.0
        assert result["total_planned"] == 0
        assert result["total_completed"] == 0
        assert result["streak_days"] == 0
        assert result["subject_stats"] == []

    async def test_perfect_week(self):
        """完美周：100% 完成率 —— 验证计算节点正确性"""
        week_start = (date.today() - timedelta(days=date.today().weekday())).strftime("%Y-%m-%d")
        week_end = (date.today() - timedelta(days=date.today().weekday()) + timedelta(days=6)).strftime("%Y-%m-%d")
        tasks = [
            {"task_date": str(date.today() - timedelta(days=i)), "subject": "数学", "estimated_minutes": 60}
            for i in range(5)
        ]
        state = {
            "user_id": "test-perfect-week",
            "week_start": week_start,
            "week_end": week_end,
            "total_plan": tasks,
            "weekly_completed": tasks,  # 全部完成
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
        result = await report_graph.ainvoke(state)

        assert result is not None
        # 纯计算节点：全部完成
        assert result["total_rate"] == 100.0
        assert result["total_completed"] == result["total_planned"]
        assert result["total_planned"] > 0

    async def test_report_html_structure(self, sample_report_state):
        """验证 HTML 周报结构完整性"""
        result = await report_graph.ainvoke(sample_report_state)

        html = result.get("html_content", "")
        if html and not result.get("error"):
            assert "<!DOCTYPE html>" in html
            assert "<html" in html
            assert "</html>" in html
            assert "备考成绩单" in html
