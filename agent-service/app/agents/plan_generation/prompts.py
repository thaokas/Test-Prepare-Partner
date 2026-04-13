"""计划生成Agent的Prompt模板"""
from typing import List


def get_foundation_level_desc(level: int) -> str:
    descs = {
        0: "零基础（对该考试领域几乎没有了解）",
        1: "有一定基础（有部分知识储备，但不够系统）",
        2: "基础扎实（知识体系较为完整，需要巩固和提升）",
    }
    return descs.get(level, "基础情况未知")


PLAN_GENERATION_PROMPT = """
你是一名专业的备考规划师。请根据以下信息为用户制定个性化的备考任务计划：

用户情况：
- 考试：{exam_name}（{exam_type}）
- 考试日期：{exam_date}（还剩{days_remaining}天）
- 当前阶段：{phase_name}
- 每日可用时间：{daily_hours}小时
- 基础水平：{foundation_level_desc}
- 薄弱科目：{weak_subjects}

考试参考信息：
{exam_info}

请生成未来{generate_days}天的每日学习任务，遵循以下原则：
1. 任务内容具体可执行，避免笼统描述
2. 薄弱科目增加约20%的学习时间
3. 零基础用户减少新知识量，增加复习频次
4. 单任务时长控制在45-90分钟
5. 基础阶段注重知识理解，强化阶段注重刷题训练，冲刺阶段注重模拟测试

只输出JSON格式的任务列表，不要包含其他文字：
[
  {{
    "task_date": "YYYY-MM-DD",
    "subject": "科目名称",
    "task_content": "具体任务描述",
    "estimated_minutes": 60,
    "task_type": 1,
    "phase": {current_phase},
    "keywords": ["关键词1", "关键词2"]
  }}
]
"""
