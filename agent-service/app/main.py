"""
FastAPI应用入口
ECNU备考搭子 - Agent服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import get_settings
from app.models.database import init_db
from app.routers import chat, plan, checkin, report
from app.scheduler.jobs import start_scheduler, shutdown_scheduler

settings = get_settings()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")

    logger.info("正在启动定时任务调度器...")
    start_scheduler()

    yield

    # 关闭时
    logger.info("正在关闭定时任务调度器...")
    shutdown_scheduler()


app = FastAPI(
    title="ECNU备考搭子 - Agent服务",
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
app.include_router(chat.router)
app.include_router(plan.router)
app.include_router(checkin.router)
app.include_router(report.router)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "ECNU备考搭子 Agent服务",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}