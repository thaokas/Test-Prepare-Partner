#!/usr/bin/env bash
set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$PROJECT_ROOT/agent-service"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

PID_LIST=()

cleanup() {
    echo ""
    echo "正在停止所有服务..."
    for pid in "${PID_LIST[@]}"; do
        kill "$pid" 2>/dev/null && echo "已停止 PID: $pid"
    done
    echo "所有服务已停止。"
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

echo "========================================"
echo "  ECNU备考搭子 - 项目启动脚本"
echo "========================================"

# ---- 1. PostgreSQL (Docker) ----
echo ""
echo "[1/4] 启动 PostgreSQL (Docker)..."
cd "$BACKEND_DIR"
docker compose up -d

echo "等待 PostgreSQL 就绪..."
until docker compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    sleep 1
done
echo "PostgreSQL 已就绪。"

# ---- 2. Agent Service ----
echo ""
echo "[2/4] 启动 Agent 服务 (FastAPI :8000)..."
cd "$AGENT_DIR"
if [ ! -f .env ]; then
    echo "警告: agent-service 下未找到 .env 文件"
fi
python main.py &
PID_LIST+=($!)
echo "Agent 服务已启动 (PID: ${PID_LIST[-1]})"

# ---- 3. Backend ----
echo ""
echo "[3/4] 启动后端服务 (Spring Boot :8080)..."
cd "$BACKEND_DIR"
if command -v mvnw &> /dev/null; then
    ./mvnw spring-boot:run &
elif command -v mvn &> /dev/null; then
    mvn spring-boot:run &
else
    echo "错误: 未找到 Maven，请安装 Maven 或使用 mvnw 包装器。"
    cleanup
    exit 1
fi
PID_LIST+=($!)
echo "后端服务已启动 (PID: ${PID_LIST[-1]})"

# ---- 4. Frontend ----
echo ""
echo "[4/4] 启动前端 (Vite :5173)..."
cd "$FRONTEND_DIR"
if [ ! -d node_modules ]; then
    echo "安装前端依赖..."
    npm install
fi
npm run dev &
PID_LIST+=($!)
echo "前端已启动 (PID: ${PID_LIST[-1]})"

echo ""
echo "========================================"
echo "  所有服务已启动！"
echo "  Agent:   http://localhost:8000"
echo "  后端:    http://localhost:8080"
echo "  前端:    http://localhost:5173"
echo "========================================"
echo "按 Ctrl+C 停止所有服务..."

wait
