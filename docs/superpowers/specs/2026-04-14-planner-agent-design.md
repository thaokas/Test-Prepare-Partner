# Planner Agent 设计文档

**日期**：2026-04-14  
**状态**：待实现  
**范围**：将 `agent-service/app/agents/plan_generation/` 重命名为 `planner/`，并完全重新设计 agent 工作流

---

## 1. 背景与目标

现有 `plan_generation` agent 是一个 4 节点线性管道（一次性生成），无法处理用户资料附件、无法追问缺失信息。

新的 **planner agent** 需要：
- 接受自然语言提示词 + 网页URL / PDF URL / 图片等附件
- 主动分析附件内容（网页抓取、PDF解析、图片理解）
- 主动追问缺失的必要信息（最多 6 轮）
- 使用网络搜索工具获取备考相关知识
- 计算用户的实际可用备考时间
- 生成全程每日备考计划（含阶段划分、科目任务、时长、休息安排）

---

## 2. 交互模型

- **模式**：多轮对话式（LangGraph `interrupt` / Human-in-the-loop）
- **输入**：自然语言提示词 + 可选附件（urls / pdf_urls / image_urls）
- **对话终止条件**：
  - 必填字段全部收集到，且 LLM 判断信息充足 → 自动开始生成
  - 已追问 6 轮 → 强制放行，用现有信息生成
- **会话标识**：每次对话携带 `thread_id`，LangGraph `MemorySaver` checkpointer 持久化中间状态

---

## 3. 必填字段

| 字段 | 说明 |
|------|------|
| `exam_name` | 考试名称，如"考研数学"、"雅思" |
| `exam_type` | 考试类型，如"考研/期末/考证/考公/语言" |
| `exam_date` | 考试日期（YYYY-MM-DD） |
| `daily_hours` | 每日可用学习时长（小时） |
| `foundation_level` | 基础水平：0-零基础 / 1-有一定基础 / 2-已复习一轮 |

LLM 可根据情况额外追问：薄弱科目、每周休息安排、偏好学习方式等。

---

## 4. State 定义

```python
class PlannerState(TypedDict):
    # ── 输入 ──────────────────────────────────────
    user_id: str
    messages: Annotated[List[BaseMessage], add_messages]  # 完整对话历史
    urls: List[str]          # 网页资料链接
    pdf_urls: List[str]      # PDF 资料链接
    image_urls: List[str]    # 图片链接

    # ── 从自然语言/资料提取的考试信息 ────────────
    exam_name: Optional[str]
    exam_type: Optional[str]
    exam_date: Optional[str]         # YYYY-MM-DD
    daily_hours: Optional[float]
    foundation_level: Optional[int]  # 0 / 1 / 2
    weak_subjects: List[str]
    rest_days_per_week: int          # 默认 1（周日）

    # ── 追问控制 ────────────────────────────────
    clarification_rounds: int         # 已追问轮数，上限 6
    clarification_question: Optional[str]  # 当前待问的问题

    # ── 资料分析 & 搜索 ───────────────────────────
    resource_summary: str   # URL/PDF/图片内容汇总
    exam_info: Dict         # 网络搜索结果

    # ── 时间计算 ─────────────────────────────────
    total_days: int
    phases: List[Dict]                # [{phase, start_date, end_date, days}]
    estimated_completion_date: str    # 可能早于 exam_date

    # ── 输出 ─────────────────────────────────────
    tasks: List[Dict]
    plan_id: Optional[str]
    message: str
    error: Optional[str]
```

---

## 5. Graph 工作流

### 5.1 节点列表

| 节点 | 类型 | 职责 |
|------|------|------|
| `parse_input_node` | LLM | 从自然语言消息提取结构化字段；正则识别 URL/PDF/图片链接 |
| `analyze_resources_node` | Tool | 抓取网页/PDF文本 + vision model 理解图片；合并为 `resource_summary` |
| `check_fields_node` | LLM | 检查必填字段；LLM 判断是否需要追问额外信息 |
| `ask_user_node` | Interrupt | `interrupt(question)` 暂停图执行；resume 后解析回复更新 state |
| `search_exam_info_node` | Tool | 搜索考试大纲、科目结构、备考建议 |
| `calculate_study_time_node` | Pure | 计算总天数、阶段划分、有效学习天数、`estimated_completion_date` |
| `generate_plan_node` | LLM | 生成全程每日任务列表（阶段 + 科目 + 时长 + 任务类型） |
| `save_plan_node` | Tool | 调用 `db_tools.create_study_plan` 写入数据库 |

### 5.2 工作流图

```
START
  │
  ▼
parse_input_node
  │
  ▼
analyze_resources_node  (仅当 urls/pdf_urls/image_urls 非空)
  │
  ▼
┌─► check_fields_node ──────────────────────────────────────┐
│     │                                                      │
│   [条件路由]                                               │
│     │                                                      │
│     ├─ needs_clarification=True & rounds < 6              │
│     │     ▼                                               │
│     │   ask_user_node                                     │
│     │     │  interrupt(question) → 返回前端               │
│     │     │  用户回复 → resume                            │
│     │     │  解析回复，更新 state，rounds += 1            │
│     └─────┘  ← 循环回到 check_fields_node                │
│                                                            │
│     └─ needs_clarification=False (信息充足 或 rounds == 6)│
│           │                                               │
└───────────┘                                               │
  ▼                                                         │
search_exam_info_node                                       │
  │                                                         │
  ▼                                                         │
calculate_study_time_node                                   │
  │                                                         │
  ▼                                                         │
generate_plan_node                                          │
  │                                                         │
  ▼                                                         │
save_plan_node                                              │
  │                                                         │
  ▼                                                         │
END                                                         │
```

### 5.3 条件路由逻辑

`analyze_resources_node` 通过条件边跳过：若 `urls + pdf_urls + image_urls` 均为空，直接进入 `check_fields_node`。

`check_fields_node` 执行后决定路由：
- `check_fields_node` 负责将 `clarification_question` 设为问题字符串（需要追问）或 `None`（信息充足）
- 路由函数读取此标志决定走向

```python
def route_after_check_fields(state: PlannerState) -> str:
    rounds_exhausted = state["clarification_rounds"] >= 6
    has_question = bool(state.get("clarification_question"))

    if has_question and not rounds_exhausted:
        return "ask_user"
    return "search_exam_info"
```

**`check_fields_node` 的设置原则**：
- 必填字段有缺失 → 生成追问缺失字段的问题，设置 `clarification_question`
- 必填字段齐全且 LLM 认为信息充足 → 设置 `clarification_question = None`
- 必填字段齐全但 LLM 希望追问补充信息 → 设置 `clarification_question`（可选追问）
- `rounds >= 6` 时 `check_fields_node` 直接设置 `clarification_question = None` 强制放行

---

## 6. 节点实现细节

### parse_input_node
- 用 LLM（structured output / function calling）从用户消息提取考试信息字段
- 用正则从消息文本中识别 `http(s)://...pdf` → `pdf_urls`，其余 http URL → `urls`，图片扩展名 → `image_urls`
- 提取到的字段写入 state，未提取到的保持 `None`

### analyze_resources_node
- **网页 URL**：`httpx.AsyncClient` 抓取 HTML → BeautifulSoup 提取正文 → LLM 摘要（限 500 字）
- **PDF URL**：下载字节流 → `pypdf.PdfReader` 提取文本 → LLM 摘要
- **图片**：传给 `get_vision_model()` 生成文字描述
- 所有摘要拼接为 `resource_summary`；若无附件则跳过此节点（条件边）

### check_fields_node
- 硬检查：4 个必填字段是否全部存在
- 若必填字段齐全，LLM 基于 `resource_summary` 和现有 state 判断是否还需要追问（如未知薄弱科目、休息安排等）
- 若判断需要追问且 `clarification_rounds < 6`，生成 `clarification_question`
- 若必填字段不全，直接生成追问缺失字段的问题

### ask_user_node
- 调用 `interrupt(state["clarification_question"])` 暂停图执行
- Resume 后，用 LLM 从用户回复中提取并更新 state 中的相关字段
- `clarification_rounds += 1`

### calculate_study_time_node
- 计算 `today → exam_date` 的总天数
- 按剩余天数划分阶段：>90天含基础阶段，30-90天含强化阶段，<30天冲刺阶段
- 计算有效学习天数（去除每周休息日）
- 根据 `daily_hours` 和考试内容量估算最短完成天数
- 若最短完成天数 < 总天数，`estimated_completion_date = today + 最短天数`，否则 = `exam_date`

### generate_plan_node
- LLM 接收全部 state 信息，生成 `today → estimated_completion_date` 的完整任务列表
- 每日任务结构：`{task_date, subject, task_content, estimated_minutes, task_type, phase}`
- 休息日：不生成任务，或仅生成 1 条轻量复习任务
- 任务类型遵循阶段原则：基础阶段侧重理解，强化阶段侧重刷题，冲刺阶段侧重模拟

### save_plan_node
- 调用 `db_tools.create_study_plan`，写入计划和任务列表
- 返回 `plan_id` 和完成消息

---

## 7. API 接口

### 新增端点：`POST /api/plan/chat`

位置：`agent-service/app/routers/plan.py`（在现有文件中追加）

```python
class PlanChatRequest(BaseModel):
    user_id: str
    thread_id: Optional[str] = None  # None = 新对话
    message: str
    urls: List[str] = []
    pdf_urls: List[str] = []
    image_urls: List[str] = []

class PlanChatResponse(BaseModel):
    thread_id: str
    status: Literal["clarifying", "complete", "error"]
    question: Optional[str]   # status=clarifying 时有值
    plan_id: Optional[str]    # status=complete 时有值
    message: str
    tasks: List[Dict] = []
```

**新对话**（`thread_id=None`）：构建 initial_state，`ainvoke` 启动图，图在 `ask_user_node` 处 interrupt 后返回 `question`

**继续对话**（`thread_id` 有值）：用 `Command(resume=message)` resume 图，继续执行直到下一次 interrupt 或 END

---

## 8. 文件结构变更

```
agent-service/app/agents/
  plan_generation/  →  【删除】
  planner/          →  【新建】
    __init__.py       # 导出 planner_graph, PlannerState
    state.py          # PlannerState 定义
    nodes.py          # 所有节点函数
    prompts.py        # 所有 prompt 模板
    graph.py          # 构建并编译 planner_graph

agent-service/app/routers/
  plan.py           →  【修改】新增 /api/plan/chat 端点，导入从 planner 改为 planner
```

---

## 9. 依赖

新增 Python 包：
- `httpx` — 异步 HTTP 客户端（抓取网页/PDF）
- `pypdf` — PDF 文本提取
- `beautifulsoup4` — HTML 正文提取

现有包复用：
- `langgraph`（`StateGraph`, `interrupt`, `MemorySaver`, `Command`）
- `langchain-openai`（`ChatOpenAI`）
- `langchain`（`tool`）

---

## 10. 不在本次范围内

- Tavily / SerpAPI 真实搜索接入（`search_exam_info` 仍为 stub，本次不改）
- 数据库 ORM 层实现（`db_tools` 仍为 stub）
- 流式 SSE 响应（本次返回完整 JSON）
- `MemorySaver` → `AsyncPostgresSaver` 升级（生产化留后续）
