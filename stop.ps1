Write-Host "正在停止所有服务..." -ForegroundColor Yellow

Get-Job | Where-Object { $_.Name -in @("AgentService", "Backend", "Frontend") } | ForEach-Object {
    Write-Host "停止 $($_.Name) (Job ID: $($_.Id))..." -ForegroundColor Gray
    Stop-Job -Job $_
    Remove-Job -Job $_
}

Write-Host "所有服务已停止。" -ForegroundColor Green
