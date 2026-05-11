#!/usr/bin/env python3
"""
交互式部署脚本 - 跨平台 (Windows / macOS / Linux)
小搭 PrepKeeper 一键部署配置工具
"""

import os
import sys
import json
import shutil
import secrets
import platform
import subprocess
from pathlib import Path

# ── 编码与颜色支持 ──────────────────────────────────────────────
if platform.system() == "Windows":
    os.system("")  # 启用 Windows 终端 ANSI 支持
    # 强制 stdout 使用 UTF-8，避免 GBK 编码报错
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


ROOT = Path(__file__).resolve().parent
AGENT_DIR = ROOT / "agent-service"
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"


def print_banner():
    print()
    print(f"{Style.CYAN}{Style.BOLD}╔══════════════════════════════════════════╗{Style.RESET}")
    print(f"{Style.CYAN}{Style.BOLD}║     小搭 PrepKeeper · 交互式部署工具     ║{Style.RESET}")
    print(f"{Style.CYAN}{Style.BOLD}╚══════════════════════════════════════════╝{Style.RESET}")
    print()


def ask(prompt: str, default: str = "", password: bool = False) -> str:
    """询问用户输入，支持默认值和密码模式"""
    suffix = f" [{default}]: " if default else ": "
    full_prompt = f"{Style.GREEN}▸{Style.RESET} {prompt}{Style.DIM}{suffix}{Style.RESET}"
    if password:
        value = _read_password(full_prompt)
    else:
        try:
            value = input(full_prompt).strip()
        except EOFError:
            print()
            sys.exit(0)
    return value if value else default


def _read_password(prompt: str) -> str:
    """跨平台密码输入"""
    try:
        import msvcrt
        print(prompt, end="", flush=True)
        chars: list[str] = []
        while True:
            try:
                ch = msvcrt.getch()
            except EOFError:
                print()
                sys.exit(0)
            if ch in (b"\r", b"\n"):
                print()
                break
            elif ch == b"\x08":  # Backspace
                if chars:
                    chars.pop()
                    print("\b \b", end="", flush=True)
            elif ch == b"\x03":  # Ctrl+C
                print()
                sys.exit(1)
            else:
                chars.append(ch.decode("utf-8", errors="ignore"))
                print("*", end="", flush=True)
        return "".join(chars)
    except ImportError:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            print(prompt, end="", flush=True)
            chars = []
            while True:
                ch = sys.stdin.read(1)
                if not ch:
                    print()
                    sys.exit(0)
                if ch in ("\r", "\n"):
                    print()
                    break
                elif ch == "\x7f":
                    if chars:
                        chars.pop()
                        print("\b \b", end="", flush=True)
                elif ch == "\x03":
                    print()
                    sys.exit(1)
                else:
                    chars.append(ch)
                    print("*", end="", flush=True)
            return "".join(chars)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def confirm(prompt: str, default: bool = True) -> bool:
    """是/否确认"""
    yn = "Y/n" if default else "y/N"
    val = ask(f"{prompt} ({yn})", "Y" if default else "N").lower()
    return val in ("y", "yes", "true", "1")


def section(title: str):
    print()
    print(f"{Style.BOLD}{Style.YELLOW}── {title} ──{Style.RESET}")


def success(msg: str):
    print(f"  {Style.GREEN}✓{Style.RESET} {msg}")


def warn(msg: str):
    print(f"  {Style.YELLOW}⚠{Style.RESET} {msg}")


def error(msg: str):
    print(f"  {Style.RED}✗{Style.RESET} {msg}")


def check_command(cmd: str) -> str | None:
    """检查命令是否可用，返回路径或 None"""
    exe = shutil.which(cmd)
    return exe


def check_prerequisites() -> dict:
    """检查前置条件"""
    section("环境检查")

    results = {}
    checks = [
        ("python", "Python 3.12+", ["python3", "python"], "--version"),
        ("java", "Java 17+", ["java"], "-version"),
        ("mvn", "Maven", ["mvn", "mvnw"], "--version"),
        ("node", "Node.js 18+", ["node"], "--version"),
        ("npm", "npm", ["npm"], "--version"),
        ("psql", "PostgreSQL 客户端", ["psql"], "--version"),
    ]

    for key, label, candidates, arg in checks:
        found = None
        for c in candidates:
            exe = check_command(c)
            if exe:
                found = exe
                break
        if found:
            try:
                output = subprocess.run(
                    [found, arg], capture_output=True, text=True, timeout=5
                ).stdout or subprocess.run(
                    [found, arg], capture_output=True, text=True, timeout=5
                ).stderr
                version_line = output.strip().split("\n")[0]
                success(f"{label}: {version_line}")
            except Exception:
                success(f"{label}: 已安装 ({found})")
            results[key] = True
        else:
            warn(f"{label}: 未找到（{key}）")
            results[key] = False

    # Docker 可选
    docker = check_command("docker")
    if docker:
        success("Docker: 已安装")
        results["docker"] = True
    else:
        results["docker"] = False

    return results


def ask_deploy_mode() -> str:
    section("部署模式")
    print(f"  {Style.DIM}1. 开发模式 - 各服务本地运行，开启 debug 和热重载{Style.RESET}")
    print(f"  {Style.DIM}2. 生产模式 - 关闭 debug，使用更严格的安全配置{Style.RESET}")
    mode = ask("选择部署模式", "1")
    return "dev" if mode == "1" else "prod"


def ask_database() -> dict:
    section("PostgreSQL 数据库配置")

    if confirm("使用 Docker 启动 PostgreSQL 容器？"):
        db_host = ask("数据库主机", "localhost")
        db_port = ask("数据库端口", "5432")
        db_name = ask("数据库名", "prepkeeper")
        db_user = ask("数据库用户名", "postgres")
        db_pass = ask("数据库密码", "", password=True) or "prepkeeper"
    else:
        db_host = ask("数据库主机", "localhost")
        db_port = ask("数据库端口", "5432")
        db_name = ask("数据库名", "prepkeeper")
        db_user = ask("数据库用户名", "postgres")
        db_pass = ask("数据库密码", "", password=True)
        if not db_pass:
            warn("数据库密码未设置，可能无法连接")

    return {
        "host": db_host,
        "port": db_port,
        "name": db_name,
        "user": db_user,
        "password": db_pass,
        "use_docker": True if db_pass == "prepkeeper" else confirm("生成 docker-compose.yml 文件？", True),
    }


def ask_llm() -> dict:
    section("LLM 大模型配置")

    provider = ask("LLM 提供商 (openai / deepseek / custom)", "openai")

    if provider == "openai":
        base_url = "https://api.openai.com/v1"
        default_model = "gpt-4o"
    elif provider == "deepseek":
        base_url = "https://api.deepseek.com/v1"
        default_model = "deepseek-chat"
    else:
        base_url = ask("LLM API Base URL", "https://api.openai.com/v1")
        default_model = "gpt-4o"

    api_key = ask("LLM API Key", "", password=True)
    if not api_key:
        warn("LLM API Key 未设置，Agent 服务将无法正常调用大模型")

    model = ask("LLM 模型名称", default_model)

    print()
    print(f"  {Style.DIM}Vision 模型用于图片理解（可选，不填写则复用 LLM 配置）{Style.RESET}")
    vision_enabled = confirm("是否独立配置 Vision 模型？", False)
    if vision_enabled:
        vision_key = ask("Vision API Key", "", password=True)
        vision_url = ask("Vision Base URL", base_url)
        vision_model = ask("Vision 模型名称", "gpt-4o")
    else:
        vision_key = ""
        vision_url = ""
        vision_model = ""

    embedding_model = ask("Embedding 模型", "text-embedding-3-small")

    return {
        "api_key": api_key,
        "base_url": base_url,
        "model": model,
        "vision_api_key": vision_key,
        "vision_base_url": vision_url,
        "vision_model": vision_model,
        "embedding_model": embedding_model,
    }


def ask_langsmith() -> dict:
    section("LangSmith 追踪（可选）")
    enabled = confirm("启用 LangSmith 调用链追踪？", False)
    if not enabled:
        return {"tracing": "false", "endpoint": "", "api_key": "", "project": ""}

    endpoint = ask("LangSmith Endpoint", "https://api.smith.langchain.com")
    api_key = ask("LangSmith API Key", "", password=True)
    project = ask("LangSmith 项目名", "prepkeeper")
    return {"tracing": "true", "endpoint": endpoint, "api_key": api_key, "project": project}


def ask_services() -> dict:
    section("服务端口配置")

    agent_host = ask("Agent 服务监听地址", "127.0.0.1")
    agent_port = ask("Agent 服务端口", "8000")
    backend_port = ask("后端服务端口", "8080")
    frontend_port = ask("前端开发服务器端口", "3000")

    jwt_secret = secrets.token_urlsafe(48)
    if confirm(f"自动生成 JWT 密钥？(随机生成，推荐)", True):
        success(f"JWT 密钥已生成: {jwt_secret[:32]}...")
    else:
        jwt_secret = ask("JWT 密钥（留空则随机生成）", "") or secrets.token_urlsafe(48)

    return {
        "agent_host": agent_host,
        "agent_port": agent_port,
        "backend_port": backend_port,
        "frontend_port": frontend_port,
        "jwt_secret": jwt_secret,
    }


def generate_agent_env(config: dict):
    """生成 agent-service/.env"""
    llm = config["llm"]
    langsmith = config["langsmith"]
    svc = config["services"]
    db = config["database"]

    lines = []
    lines.append("# 由 deploy.py 自动生成")
    lines.append("")
    lines.append("# Database")
    lines.append(f"DATABASE_URL=postgresql://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['name']}")
    lines.append("")
    lines.append("# LLM Configuration")
    lines.append(f"LLM_API_KEY={llm['api_key']}")
    lines.append(f"LLM_BASE_URL={llm['base_url']}")
    lines.append(f"LLM_MODEL={llm['model']}")
    if llm["vision_api_key"]:
        lines.append(f"VISION_API_KEY={llm['vision_api_key']}")
        lines.append(f"VISION_BASE_URL={llm['vision_base_url']}")
        lines.append(f"VISION_MODEL={llm['vision_model']}")
    lines.append("")
    lines.append("# Embedding Model")
    lines.append(f"EMBEDDING_MODEL={llm['embedding_model']}")
    lines.append("")
    lines.append("# LangSmith Tracing")
    lines.append(f"LANGSMITH_TRACING={langsmith['tracing']}")
    if langsmith["tracing"] == "true":
        lines.append(f"LANGSMITH_ENDPOINT={langsmith['endpoint']}")
        lines.append(f"LANGSMITH_API_KEY={langsmith['api_key']}")
        lines.append(f"LANGSMITH_PROJECT={langsmith['project']}")
    lines.append("")
    lines.append("# Server")
    lines.append(f"HOST={svc['agent_host']}")
    lines.append(f"PORT={svc['agent_port']}")
    lines.append(f"DEBUG={'true' if config['mode'] == 'dev' else 'false'}")

    env_path = AGENT_DIR / ".env"
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    success(f"已生成 {env_path.relative_to(ROOT)}")


def generate_backend_yml(config: dict):
    """生成 backend application.yml"""
    svc = config["services"]
    db = config["database"]
    mode = config["mode"]

    yml = f"""# 由 deploy.py 自动生成
spring:
  application:
    name: prep-keeper-backend

  datasource:
    url: jdbc:postgresql://{db['host']}:{db['port']}/{db['name']}
    username: {db['user']}
    password: {db['password']}
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 10
      minimum-idle: 5
      idle-timeout: 300000
      connection-timeout: 20000

  jpa:
    hibernate:
      ddl-auto: update
    show-sql: {'true' if mode == 'dev' else 'false'}
    open-in-view: false

server:
  port: {svc['backend_port']}

jwt:
  secret: {svc['jwt_secret']}
  expiration: 86400000
  refresh-expiration: 604800000

agent:
  service:
    url: http://{svc['agent_host']}:{svc['agent_port']}
    timeout: 30000
    retry: 3

springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
"""

    yml_path = BACKEND_DIR / "src" / "main" / "resources" / "application.yml"
    yml_path.parent.mkdir(parents=True, exist_ok=True)
    yml_path.write_text(yml, encoding="utf-8")
    success(f"已生成 {yml_path.relative_to(ROOT)}")


def generate_docker_compose(config: dict):
    """生成 backend/docker-compose.yml（如果用户需要）"""
    db = config["database"]
    if not db.get("use_docker"):
        return

    dc = f"""# 由 deploy.py 自动生成
services:
  postgres:
    image: postgres:16-alpine
    container_name: prepkeeper-db
    environment:
      POSTGRES_DB: {db['name']}
      POSTGRES_USER: {db['user']}
      POSTGRES_PASSWORD: {db['password']}
    ports:
      - "{db['port']}:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {db['user']}"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

volumes:
  postgres_data:
"""

    dc_path = BACKEND_DIR / "docker-compose.yml"
    dc_path.write_text(dc, encoding="utf-8")
    success(f"已生成 {dc_path.relative_to(ROOT)}")


def generate_frontend_env(config: dict):
    """生成前端环境配置"""
    svc = config["services"]
    env_content = f"""# 由 deploy.py 自动生成
VITE_API_BASE_URL=http://localhost:{svc['backend_port']}
"""

    env_path = FRONTEND_DIR / ".env"
    env_path.write_text(env_content, encoding="utf-8")
    success(f"已生成 {env_path.relative_to(ROOT)}")


def generate_run_scripts(config: dict):
    """生成各平台的启动脚本"""

    agent_host = config["services"]["agent_host"]
    agent_port = config["services"]["agent_port"]

    # ── Linux/macOS start script ──
    sh_path = ROOT / "start.sh"
    sh_content = f"""#!/usr/bin/env bash
set -e
echo "===== 小搭 PrepKeeper 启动 ====="

# 1. PostgreSQL（Docker）
if [ -f backend/docker-compose.yml ]; then
  echo "[1/3] 启动 PostgreSQL..."
  cd backend && docker compose up -d && cd ..
fi

# 2. Agent 服务
echo "[2/3] 启动 Agent 服务..."
cd agent-service
if [ ! -d .venv ]; then
  pip install uv 2>/dev/null || pip3 install uv
  uv sync
fi
uv run uvicorn app.main:app --host {agent_host} --port {agent_port} &
AGENT_PID=$!
cd ..

# 3. 后端
echo "[3/3] 启动后端..."
cd backend && mvn spring-boot:run &
BACKEND_PID=$!
cd ..

echo
echo "✓ Agent 服务: http://{agent_host}:{agent_port}/docs"
echo "✓ 后端服务: http://localhost:{config['services']['backend_port']}/swagger-ui.html"
echo "✓ 前端（手动启动）: cd frontend && npm install && npm run dev"
echo
echo "按 Ctrl+C 停止所有服务"
trap "kill $AGENT_PID $BACKEND_PID 2>/dev/null; exit" INT TERM
wait
"""
    sh_path.write_text(sh_content, encoding="utf-8", newline="\n")
    sh_path.chmod(0o755)
    success(f"已生成 {sh_path.relative_to(ROOT)}")

    # ── Windows start script ──
    bat_path = ROOT / "start.bat"
    bat_content = f"""@echo off
chcp 65001 >nul
echo ===== 小搭 PrepKeeper 启动 =====

REM 1. PostgreSQL (Docker)
if exist backend\\docker-compose.yml (
    echo [1/3] 启动 PostgreSQL...
    cd backend && docker compose up -d && cd ..
)

REM 2. Agent 服务
echo [2/3] 启动 Agent 服务...
start "Agent-Service" cmd /k "cd agent-service && uv run uvicorn app.main:app --host {agent_host} --port {agent_port}"

REM 3. 后端
echo [3/3] 启动后端...
start "Backend" cmd /k "cd backend && mvn spring-boot:run"

echo.
echo ✓ Agent 服务: http://{agent_host}:{agent_port}/docs
echo ✓ 后端服务: http://localhost:{config['services']['backend_port']}/swagger-ui.html
echo ✓ 前端（手动启动）: cd frontend ^&^& npm install ^&^& npm run dev
echo.
pause
"""
    bat_path.write_text(bat_content, encoding="utf-8", newline="\r\n")
    success(f"已生成 {bat_path.relative_to(ROOT)}")


def print_summary(config: dict):
    """打印配置摘要"""
    svc = config["services"]
    db = config["database"]
    llm = config["llm"]

    section("部署配置摘要")

    print(f"  部署模式:     {Style.BOLD}{config['mode']}{Style.RESET}")
    print(f"  数据库:       {db['host']}:{db['port']}/{db['name']}")
    print(f"  LLM 模型:     {llm['model']}")
    print(f"  Agent 服务:   http://{svc['agent_host']}:{svc['agent_port']}")
    print(f"  后端服务:     http://localhost:{svc['backend_port']}")
    print(f"  前端端口:     {svc['frontend_port']}")
    print()

    section("启动命令")

    is_win = platform.system() == "Windows"

    print(f"  {Style.BOLD}1. 启动 PostgreSQL 数据库{Style.RESET}")
    if db.get("use_docker"):
        print(f"     cd backend && docker compose up -d")
    else:
        print(f"     (请确保 PostgreSQL 服务已运行)")
    print()
    print(f"  {Style.BOLD}2. 启动 Agent 服务{Style.RESET}")
    print(f"     cd agent-service")
    if not (AGENT_DIR / ".venv").exists():
        print(f"     pip install uv && uv sync")
    print(f"     uv run uvicorn app.main:app --host {svc['agent_host']} --port {svc['agent_port']}{' --reload' if config['mode'] == 'dev' else ''}")
    print()
    print(f"  {Style.BOLD}3. 启动后端服务{Style.RESET}")
    print(f"     cd backend && mvn spring-boot:run")
    print()
    print(f"  {Style.BOLD}4. 启动前端{Style.RESET}")
    if not (FRONTEND_DIR / "node_modules").exists():
        print(f"     cd frontend && npm install")
    print(f"     cd frontend && npm run dev")
    print()

    if not is_win:
        print(f"  {Style.DIM}或直接运行: ./start.sh{Style.RESET}")
    else:
        print(f"  {Style.DIM}或双击运行: start.bat{Style.RESET}")
    print()


def save_config_json(config: dict):
    """将配置保存为 JSON（方便 CI/CD 或后续使用）"""
    # 不序列化密码相关字段到 JSON（安全考虑）
    safe_config = {
        "mode": config["mode"],
        "services": {
            "agent_host": config["services"]["agent_host"],
            "agent_port": config["services"]["agent_port"],
            "backend_port": config["services"]["backend_port"],
            "frontend_port": config["services"]["frontend_port"],
        },
        "database": {
            "host": config["database"]["host"],
            "port": config["database"]["port"],
            "name": config["database"]["name"],
        },
        "llm": {
            "model": config["llm"]["model"],
            "base_url": config["llm"]["base_url"],
            "embedding_model": config["llm"]["embedding_model"],
        },
    }
    deploy_json = ROOT / ".deploy.json"
    deploy_json.write_text(json.dumps(safe_config, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    print_banner()

    # 1. 环境检查
    prereqs = check_prerequisites()
    missing = [k for k, v in prereqs.items() if not v and k != "docker"]
    if missing:
        print()
        warn(f"缺少以下依赖: {', '.join(missing)}，相关服务可能无法启动")

    # 2. 收集配置
    config = {}
    config["mode"] = ask_deploy_mode()
    config["database"] = ask_database()
    config["llm"] = ask_llm()
    config["langsmith"] = ask_langsmith()
    config["services"] = ask_services()

    # 3. 确认
    section("确认")
    print()
    print(f"  部署模式: {config['mode']}")
    print(f"  数据库:   {config['database']['host']}:{config['database']['port']}/{config['database']['name']}")
    print(f"  LLM:      {config['llm']['model']} @ {config['llm']['base_url']}")
    print(f"  Agent:    http://{config['services']['agent_host']}:{config['services']['agent_port']}")
    print(f"  后端:     http://localhost:{config['services']['backend_port']}")
    print(f"  前端:     端口 {config['services']['frontend_port']}")
    print()

    if not confirm("确认以上配置？选择 No 将重新开始", True):
        print(f"{Style.YELLOW}已取消，重新开始...{Style.RESET}")
        return main()

    # 4. 生成配置文件
    print()
    section("生成配置文件")
    generate_agent_env(config)
    generate_backend_yml(config)
    generate_docker_compose(config)
    generate_frontend_env(config)
    generate_run_scripts(config)
    save_config_json(config)

    # 5. 打印摘要
    print_summary(config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Style.YELLOW}部署配置已取消{Style.RESET}")
        sys.exit(0)
