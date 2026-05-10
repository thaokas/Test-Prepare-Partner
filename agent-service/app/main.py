"""
FastAPI应用入口
小搭 - Agent服务
"""
import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import plan, checkin, reminder, report

settings = get_settings()

# 确保 logs 目录存在
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(logs_dir / "app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# 初始化 LangSmith 调用链追踪
if os.getenv("LANGSMITH_TRACING") in ("true", "True", "1"):
    import langsmith
    os.environ.setdefault("LANGSMITH_TRACING_V2", "true")
    logger.info(
        "LangSmith tracing 已启用 | Project: %s | Endpoint: %s",
        os.getenv("LANGSMITH_PROJECT", "default"),
        os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""

    logger.info("正在启动...")
    yield
    logger.info("正在关闭...")


app = FastAPI(
    title="小搭 - Agent服务",
    description="基于LangChain/LangGraph的智能备考督导Agent",
    version="0.1.0",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(plan.router)
app.include_router(checkin.router)
app.include_router(reminder.router)
app.include_router(report.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "小搭 Agent服务",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}