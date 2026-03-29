# ECNU备考搭子 - Agent服务

基于 LangChain/LangGraph 的智能备考督导Agent服务。

## 快速开始

### 1. 安装依赖

```bash
cd agent-service
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/prepkeeper
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4
```

### 3. 创建数据库

```sql
CREATE DATABASE prepkeeper;
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档。

## 项目结构

```
agent-service/
├── app/
│   ├── main.py              # FastAPI入口
│   ├── config.py            # 配置管理
│   ├── routers/             # API路由
│   │   ├── chat.py          # 对话接口
│   │   ├── plan.py          # 计划相关
│   │   ├── checkin.py       # 打卡相关
│   │   └── report.py        # 周报相关
│   ├── models/              # SQLAlchemy模型
│   ├── graphs/              # LangGraph工作流
│   ├── tools/               # LangChain工具
│   ├── rag/                 # RAG检索
│   ├── scheduler/           # 定时任务
│   └── utils/               # 工具函数
├── tests/                   # 测试文件
├── requirements.txt
└── .env.example
```

## API接口

### POST /api/chat
对话入口

### POST /api/plan/generate
生成备考计划

### POST /api/checkin
打卡处理

### GET /api/plan/today
获取今日任务

### GET /api/report/weekly
获取周报

## 核心工作流

1. **计划生成流程**: 计算阶段 → 生成任务 → 保存计划
2. **打卡处理流程**: 解析内容 → 匹配任务 → 更新进度 → 生成鼓励
3. **提醒流程**: 查询未完成 → 选择模板 → 发送提醒
4. **周报流程**: 聚合数据 → 计算指标 → 生成总结

## 测试

```bash
pytest tests/ -v
```