$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$AgentDir    = Join-Path $ProjectRoot "agent-service"
$BackendDir  = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"

$Jobs = @()

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ECNU备考搭子 - 项目启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ---- 1. PostgreSQL (Docker) ----
Write-Host "`n[1/4] 启动 PostgreSQL (Docker)..." -ForegroundColor Yellow
Push-Location $BackendDir
docker compose up -d

Write-Host "等待 PostgreSQL 就绪..."
do {
    Start-Sleep -Seconds 2
    $healthy = docker compose exec -T postgres pg_isready -U postgres 2>$null
} while ($LASTEXITCODE -ne 0)
Write-Host "PostgreSQL 已就绪。" -ForegroundColor Green
Pop-Location

# ---- 2. Agent Service ----
Write-Host "`n[2/4] 启动 Agent 服务 (FastAPI :8000)..." -ForegroundColor Yellow
Push-Location $AgentDir
if (-not (Test-Path ".env")) {
    Write-Host "警告: agent-service 下未找到 .env 文件" -ForegroundColor DarkYellow
}
$agentJob = Start-Job -Name "AgentService" -ScriptBlock {
    Set-Location $using:AgentDir
    python main.py
}
$Jobs += $agentJob
Write-Host "Agent 服务已启动 (Job ID: $($agentJob.Id))" -ForegroundColor Green
Pop-Location

# ---- 3. Backend ----
Write-Host "`n[3/4] 启动后端服务 (Spring Boot :8080)..." -ForegroundColor Yellow
Push-Location $BackendDir
$mvnCmd = if (Test-Path ".\mvnw.cmd") { ".\mvnw.cmd" } elseif (Get-Command mvn -ErrorAction SilentlyContinue) { "mvn" } else { $null }
if (-not $mvnCmd) {
    Write-Host "错误: 未找到 Maven，请安装 Maven 或使用 mvnw 包装器。" -ForegroundColor Red
    Stop-Job -Job $Jobs
    Remove-Job -Job $Jobs
    Pop-Location
    exit 1
}
$backendJob = Start-Job -Name "Backend" -ScriptBlock {
    Set-Location $using:BackendDir
    & $using:mvnCmd spring-boot:run
}
$Jobs += $backendJob
Write-Host "后端服务已启动 (Job ID: $($backendJob.Id))" -ForegroundColor Green
Pop-Location

# ---- 4. Frontend ----
Write-Host "`n[4/4] 启动前端 (Vite :5173)..." -ForegroundColor Yellow
Push-Location $FrontendDir
if (-not (Test-Path "node_modules")) {
    Write-Host "安装前端依赖..."
    npm install
}
$frontendJob = Start-Job -Name "Frontend" -ScriptBlock {
    Set-Location $using:FrontendDir
    npm run dev
}
$Jobs += $frontendJob
Write-Host "前端已启动 (Job ID: $($frontendJob.Id))" -ForegroundColor Green
Pop-Location

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  所有服务已启动！" -ForegroundColor Cyan
Write-Host "  Agent:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  后端:    http://localhost:8080" -ForegroundColor Cyan
Write-Host "  前端:    http://localhost:5173" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n运行 .\stop.ps1 停止所有服务，或直接关闭此窗口。" -ForegroundColor Gray
Write-Host "按 Ctrl+C 也会尝试清理后台作业..." -ForegroundColor Gray

try {
    while ($true) {
        Start-Sleep -Seconds 2
        $running = $Jobs | Where-Object { $_.State -eq "Running" }
        if (-not $running) {
            break
        }
    }
} finally {
    Write-Host "`n正在停止所有服务..." -ForegroundColor Yellow
    foreach ($job in $Jobs) {
        Stop-Job -Job $job -ErrorAction SilentlyContinue
        Remove-Job -Job $job -ErrorAction SilentlyContinue
    }
    Write-Host "所有服务已停止。" -ForegroundColor Green
}
