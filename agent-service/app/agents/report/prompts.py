"""周报生成Agent节点函数"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict

from app.agents.report.state import ReportState

logger = logging.getLogger(__name__)

ANALYZE_PROMPT = """
你是备考督导助手，请分析用户本周的学习表现。

本周数据：
- 平均完成率：{average_rate}%
- 环比上周：{week_over_week:+.1f}%
- 连续打卡：{current_streak}天
- 每日完成率：{daily_rates}

请分析亮点和问题，输出JSON格式：
{{
  "highlights": ["亮点1", "亮点2"],
  "issues": ["问题1", "问题2"]
}}
"""

SUMMARY_PROMPT = """
你是备考督导助手"小搭"，请为用户生成一份温暖的周报总结。

本周表现：
- 平均完成率：{average_rate}%
- 亮点：{highlights}
- 问题：{issues}

请生成3-5句话的周报总结，语气积极鼓励，指出用户的进步和需要改进的地方。
直接输出总结文本。
"""

SUGGESTIONS_PROMPT = """
根据用户本周表现，给出下周的3条具体改进建议：

- 平均完成率：{average_rate}%
- 主要问题：{issues}

每条建议要具体可执行。
只输出JSON数组格式：["建议1", "建议2", "建议3"]
"""
