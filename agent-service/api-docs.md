# 小搭 Agent服务 API 文档

**版本**: 0.1.0 | **Base URL**: `http://127.0.0.1:8000`

---

## 通用说明

- **Content-Type**: `application/json`
- **CORS**: 所有来源允许（开发环境）
- **健康检查**: `GET /health` → `{"status": "healthy"}`

---

## 1. 打卡模块 (Checkin)

### `POST /api/checkin/`

处理用户打卡，LLM 根据完成内容生成一句鼓励文案。

**Request Body:**

```json
{
  "completed_content": "完成了高数第三章不定积分的学习和习题",
  "overall_completion_rate": 45.0,
  "image_url": null
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `completed_content` | string | 是 | 今日完成的计划内容描述 |
| `overall_completion_rate` | float | 是 | 整体备考计划完成比例（0-100） |
| `image_url` | string \| null | 否 | 打卡截图/图片URL，传入则先由多模态模型总结 |

**Response `200`:**

```json
{
  "encouragement": "不定积分拿下啦，线性代数也在向你招手，稳扎稳打！"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `encouragement` | string | 一句简短鼓励，不超过30字 |

**工作流**: `image_url` 非空时先走 `summarize_image`（多模态摘要）再 `generate_encouragement`，无图片直接生成鼓励。

---

## 2. 备考计划模块 (Plan)

### `POST /api/plan/chat`

多轮对话式备考计划生成，支持人工追问。

**Request Body:**

```json
{
  "user_id": "user-001",
  "message": "我要备考考研数学一，零基础，每天能学3小时",
  "thread_id": null,
  "urls": [],
  "pdf_urls": [],
  "image_urls": []
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户ID |
| `message` | string | 是 | 用户输入的自然语言描述 |
| `thread_id` | string \| null | 否 | 续聊时传入已有thread_id；新对话传null |
| `urls` | string[] | 否 | 参考资料网页URL |
| `pdf_urls` | string[] | 否 | PDF资料URL |
| `image_urls` | string[] | 否 | 图片资料URL |

**Response `200` — 等待追问 (waiting_for_input):**

```json
{
  "thread_id": "abc-123",
  "status": "waiting_for_input",
  "message": "请问你的考试日期是什么时候？",
  "clarification_question": "请问你的考试日期是什么时候？",
  "plan_id": null,
  "tasks": []
}
```

**Response `200` — 生成完成 (completed):**

```json
{
  "thread_id": "abc-123",
  "status": "completed",
  "message": "备考计划已生成！共 45 个学习任务，祝你考试顺利！",
  "clarification_question": null,
  "plan_id": "plan-efgh-456",
  "tasks": [
    {
      "task_date": "2026-05-10",
      "subject": "高等数学",
      "task_content": "学习第一章函数与极限",
      "estimated_minutes": 60,
      "task_type": 1,
      "phase": 1
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `thread_id` | string | 线程ID，续聊时回传 |
| `status` | string | `waiting_for_input` — 需追问 / `completed` — 生成完成 / `error` — 出错 |
| `message` | string | 状态描述或追问问题 |
| `clarification_question` | string \| null | 追问问题文本 |
| `plan_id` | string \| null | 计划ID（完成时有值） |
| `tasks` | array | 每日任务列表（完成时有值） |

**工作流**: `parse_input → analyze_resources → check_fields → [追问循环] → search_exam_info → calculate_study_time → generate_plan → save_plan`

追问最多6轮，必填字段（exam_name / exam_type / exam_date / daily_hours / foundation_level）任一缺失会触发追问。

**续聊示例**:

```json
// 第一次调用（新对话）
{"user_id": "user-001", "message": "我要备考考研数学一", "thread_id": null}

// 回复追问（续聊）
{"user_id": "user-001", "message": "12月20日考试，每天3小时", "thread_id": "abc-123"}
```

---

### `POST /api/plan/generate`

一次性生成备考计划（不追问，兼容旧接口）。

**Request Body:**

```json
{
  "user_id": "user-001",
  "exam_name": "考研数学一",
  "exam_type": "考研",
  "exam_date": "2026-12-20",
  "daily_hours": 3.0,
  "foundation_level": 0,
  "weak_subjects": ["线性代数"]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户ID |
| `exam_name` | string | 是 | 考试名称 |
| `exam_type` | string | 是 | 考试类型：考研/期末/考证/考公/语言/期中 |
| `exam_date` | string | 是 | 考试日期 YYYY-MM-DD |
| `daily_hours` | float | 是 | 每日可用时长（小时），>0 且 ≤24 |
| `foundation_level` | int | 是 | 0=零基础, 1=有一定基础, 2=已复习一轮 |
| `weak_subjects` | string[] | 否 | 薄弱科目列表 |

**Response `200`:**

```json
{
  "plan_id": "plan-efgh-456",
  "total_tasks": 45,
  "message": "备考计划已生成！共 45 个学习任务，祝你考试顺利！",
  "tasks": [...]
}
```

---

### `GET /api/plan/today?user_id={user_id}`

获取用户今日任务。

**Query Parameters:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户ID |

**Response `200`:**

```json
{
  "tasks": [],
  "total": 0
}
```

---

## 3. 提醒模块 (Reminder)

### `POST /api/reminder/generate`

根据任务进度和严格度模式，LLM 生成个性化提醒文案。

**Request Body:**

```json
{
  "today_total_tasks": [
    {"subject": "数学", "name": "习题", "estimated_minutes": 60}
  ],
  "today_incomplete_tasks": [
    {"subject": "数学", "name": "习题", "estimated_minutes": 60}
  ],
  "exam_total_tasks": [{"id": "1"}, {"id": "2"}],
  "exam_completed_tasks": [],
  "elapsed_study_days": 10.0,
  "total_study_days": 90.0,
  "strictness_mode": "gentle"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `today_total_tasks` | array | 是 | 今日全部任务 |
| `today_incomplete_tasks` | array | 是 | 今日未完成任务 |
| `exam_total_tasks` | array | 是 | 备考全部任务 |
| `exam_completed_tasks` | array | 是 | 备考已完成任务 |
| `elapsed_study_days` | float | 是 | 已消耗备考天数 |
| `total_study_days` | float | 是 | 备考总天数 |
| `strictness_mode` | string | 是 | 严格模式：`silent` / `gentle` / `intensive` / `nightmare` / `tangseng` |

**Response `200`:**

```json
{
  "content": "今天还有数学的习题没完成哦，抓紧时间吧！"
}
```

**严格模式说明:**

| 模式 | 字数 | 风格 |
|------|------|------|
| `silent` | 0 | 静默，不发送提醒 |
| `gentle` | 60-100 | 温暖肯定，柔性提醒 |
| `intensive` | 80-120 | 坚定督促，强调紧迫 |
| `nightmare` | 100-150 | 尖锐毒舌，揭穿借口 |
| `tangseng` | 200-300 | 唐僧式唠叨，反复催促 |

---

### `GET /api/reminder/settings/{user_id}`

获取用户提醒设置。

**Response `200`:**

```json
{
  "mode": 1,
  "custom_times": [],
  "monking_interval": 30,
  "is_active": true
}
```

---

### `PUT /api/reminder/settings/{user_id}`

更新用户提醒设置。

**Request Body:**

```json
{
  "mode": 1,
  "custom_times": ["09:00", "14:00", "20:00"],
  "monking_interval": 30
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | int | 是 | 0=静默, 1=温柔, 2=强化, 3=唐僧 |
| `custom_times` | string[] | 否 | 自定义提醒时间 |
| `monking_interval` | int | 是 | 唐僧模式间隔（分钟，5-120） |

---

## 4. 周报模块 (Report)

### `POST /api/report/weekly`

生成HTML格式的备考周报。

**Request Body:**

```json
{
  "user_id": "user-001",
  "week_start": "2026-05-04",
  "week_end": null,
  "total_plan": [
    {"task_date": "2026-05-04", "subject": "数学", "estimated_minutes": 60}
  ],
  "weekly_completed": [
    {"task_date": "2026-05-04", "subject": "数学", "estimated_minutes": 60}
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `user_id` | string | 是 | 用户ID |
| `week_start` | string | 是 | 周一日期 YYYY-MM-DD |
| `week_end` | string \| null | 否 | 周日日期，不传则自动推算 |
| `total_plan` | array | 是 | 本周计划任务列表 |
| `weekly_completed` | array | 是 | 本周已完成任务列表 |

**任务对象结构:**

```json
{
  "task_date": "2026-05-04",
  "subject": "科目名称",
  "estimated_minutes": 60
}
```

**Response `200`:**

```json
{
  "report_id": "rpt-abc-789",
  "user_id": "user-001",
  "week_start": "2026-05-04",
  "week_end": "2026-05-10",
  "total_rate": 60.0,
  "html_content": "<!DOCTYPE html><html>...</html>",
  "summary": "本周完成率 60.0%，完成 6/10 项任务，学习 5.0 小时，打卡 5 天。"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `report_id` | string \| null | 周报ID |
| `total_rate` | float | 总完成率（0-100） |
| `html_content` | string | 完整HTML周报，移动端适配卡片布局 |
| `summary` | string | 纯文字摘要，供HTML不可用时降级展示 |

**工作流**: `calculate_metrics → analyze_performance → generate_html_report → save_report`

**HTML周报包含**: 总览卡片（完成率进度条、任务数、学习时长、打卡天数）、各科明细表、亮点与待改进分析、风趣点评、下周建议。

---

## 5. 系统接口

### `GET /`

服务信息。

```json
{
  "name": "小搭 Agent服务",
  "version": "0.1.0",
  "status": "running"
}
```

### `GET /health`

健康检查。

```json
{"status": "healthy"}
```

### `GET /docs`

Swagger UI 交互文档（由 FastAPI 自动生成）。

### `GET /openapi.json`

OpenAPI 3.0 规范文件。

---

## 架构说明

```
前端 (React) → 后端 (Spring Boot) → Agent服务 (FastAPI + LangGraph)
                                       ├── Checkin Agent   → LLM 多模态/纯文本
                                       ├── Planner Agent   → LLM + 搜索工具
                                       ├── Reminder Agent  → LLM + 工具调用
                                       ├── Report Agent    → LLM + 计算
                                       ├── RAG 知识库       → 鼓励话术/备考策略/彩蛋
                                       └── 搜索工具         → (预留，当前为存根)
```

- Agent 不直接与数据库交互，DB操作由后端处理
- 知识库使用本地JSON文件检索（鼓励话术、考试策略、彩蛋、闲聊）
- LLM 支持任何 OpenAI API 兼容接口
