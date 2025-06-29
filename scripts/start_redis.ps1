# Script para iniciar Redis via Docker Compose
Set-Location "C:\Users\pedro\Agente AI Gestor de Obras"
Write-Host "Iniciando Redis via Docker Compose..." -ForegroundColor Cyan
docker-compose up -d redis
Write-Host "Aguardando Redis iniciar..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
Write-Host "Verificando status..." -ForegroundColor Green
docker ps --filter name=obras_redis
