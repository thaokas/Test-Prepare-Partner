from .db_tools import DB_TOOLS
from .search_tools import SEARCH_TOOLS
from .rag_tools import RAG_TOOLS

# 按Agent分组导出
PLAN_TOOLS = DB_TOOLS[:3] + SEARCH_TOOLS        # get_user_profile, get_active_plan, create_study_plan + 搜索工具
CHECKIN_TOOLS = DB_TOOLS[3:10] + RAG_TOOLS      # 任务/打卡相关工具 + RAG
REMINDER_TOOLS = [DB_TOOLS[10]] + RAG_TOOLS     # get_reminder_settings + RAG
REPORT_TOOLS = DB_TOOLS[12:] + RAG_TOOLS        # get_weekly_data, save_weekly_report + RAG

ALL_TOOLS = DB_TOOLS + SEARCH_TOOLS + RAG_TOOLS

__all__ = [
    "DB_TOOLS", "SEARCH_TOOLS", "RAG_TOOLS",
    "PLAN_TOOLS", "CHECKIN_TOOLS", "REMINDER_TOOLS", "REPORT_TOOLS",
    "ALL_TOOLS",
]
