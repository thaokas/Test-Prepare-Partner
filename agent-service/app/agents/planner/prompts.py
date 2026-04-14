"""Planner Agent 所有 Prompt 模板"""


PARSE_INPUT_PROMPT = """从用户的备考需求描述中提取以下信息，以 JSON 格式返回。未提及的字段返回 null。

用户消息：
{message}

参考资料摘要（如有）：
{resource_summary}

基础水平说明：0=零基础（几乎没有了解），1=有一定基础（有部分知识储备），2=已复习一轮（知识体系较完整）

以 JSON 格式返回（字段可为 null）：
{{
  "exam_name": "考试名称（如考研数学、雅思）或 null",
  "exam_type": "考试类型（考研/期末/考证/考公/语言/其他）或 null",
  "exam_date": "考试日期 YYYY-MM-DD 格式或 null",
  "daily_hours": 每日可用学习时长数字（小时）或 null,
  "foundation_level": 基础水平 0/1/2 整数或 null,
  "weak_subjects": ["薄弱科目列表，无则为空数组"],
  "rest_days_per_week": 每周休息天数整数（默认 1）或 null,
  "urls": ["从消息中识别的非PDF网页URL列表"],
  "pdf_urls": ["从消息中识别的PDF URL列表（含.pdf后缀）"],
  "image_urls": ["从消息中识别的图片URL列表（含.jpg/.png/.jpeg/.webp）"]
}}

只输出 JSON，不要包含其他文字。"""


CHECK_FIELDS_PROMPT = """你是一名备考规划师助手，正在为用户制定备考计划。

已收集的信息：
- 考试名称：{exam_name}
- 考试类型：{exam_type}
- 考试日期：{exam_date}
- 每日可用时间：{daily_hours} 小时
- 基础水平：{foundation_level_desc}
- 薄弱科目：{weak_subjects}
- 每周休息天数：{rest_days_per_week}

参考资料摘要：
{resource_summary}

已追问轮数：{clarification_rounds} / 6

任务：判断是否需要向用户追问更多信息。规则：
1. exam_name、exam_type、exam_date、daily_hours、foundation_level 任意一个为 null，必须追问对应字段
2. 必填字段已齐全时，若追问薄弱科目或每周休息安排能显著提升计划质量，可选择追问
3. 若追问轮数已达 6，无论信息是否充足，返回 needs_clarification: false

以 JSON 格式返回：
{{
  "needs_clarification": true 或 false,
  "question": "要问用户的问题（needs_clarification=true 时填写，否则为 null）"
}}

只输出 JSON，不要包含其他文字。"""


PARSE_REPLY_PROMPT = """用户回复了你的追问。从回复中提取备考信息。

已有信息：
- 考试名称：{exam_name}
- 考试类型：{exam_type}
- 考试日期：{exam_date}
- 每日时间：{daily_hours}
- 基础水平：{foundation_level}
- 薄弱科目：{weak_subjects}

你的追问：{question}
用户回复：{reply}

以 JSON 格式返回从本次回复中新提取的信息（未提及的字段返回 null）：
{{
  "exam_name": null,
  "exam_type": null,
  "exam_date": null,
  "daily_hours": null,
  "foundation_level": null,
  "weak_subjects": null,
  "rest_days_per_week": null
}}

只输出 JSON，不要包含其他文字。"""


GENERATE_PLAN_PROMPT = """你是一名专业备考规划师。请根据以下信息为用户制定完整的每日备考计划。

用户情况：
- 考试：{exam_name}（{exam_type}）
- 考试日期：{exam_date}
- 计划开始日期：{start_date}
- 计划结束日期：{estimated_completion_date}
- 每日可用时间：{daily_hours} 小时
- 基础水平：{foundation_level_desc}
- 薄弱科目：{weak_subjects}
- 每周休息天数：{rest_days_per_week}（默认周日为休息日）

备考阶段安排：
{phases_desc}

考试参考信息：
{exam_info}

参考资料摘要：
{resource_summary}

请生成从 {start_date} 到 {estimated_completion_date} 的每日学习任务（共约 {total_plan_days} 天）：

规则：
1. 周日（rest day）：不生成任务
2. 单任务时长控制在 45-90 分钟
3. 薄弱科目增加约 20% 时间
4. 基础阶段侧重理解，强化阶段侧重刷题，冲刺阶段侧重模拟测试
5. 每日任务数量根据 daily_hours 决定，不超过 daily_hours * 60 / 45 个任务
6. 任务类型：1=学习新内容 2=复习 3=刷题练习 4=模拟测试

只输出 JSON 数组，不要包含其他文字：
[
  {{
    "task_date": "YYYY-MM-DD",
    "subject": "科目名称",
    "task_content": "具体可执行的任务描述",
    "estimated_minutes": 60,
    "task_type": 1,
    "phase": 1
  }}
]"""


RESOURCE_SUMMARY_PROMPT = """请将以下资料内容提炼为简洁摘要（不超过 300 字），重点提取与备考相关的信息（考试大纲、科目、重点、时间安排等）。

资料内容：
{content}

只输出摘要文字，不要包含其他内容。"""


def get_foundation_level_desc(level: int | None) -> str:
    from typing import Optional
    descs = {
        0: "零基础（对该考试领域几乎没有了解）",
        1: "有一定基础（有部分知识储备，但不够系统）",
        2: "已复习一轮（知识体系较为完整，需要巩固和提升）",
    }
    return descs.get(level, "基础情况未知") if level is not None else "未知"
