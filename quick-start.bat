@echo off
chcp 65001 >nul
echo ============================================
echo 小智笔记 - 快速启动（使用已导入的镜像）
echo ============================================
echo.

REM 检查 Docker 是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause
    exit /b 1
)

echo [1/3] 检查镜像...
echo.

REM 检查必需的镜像
set MISSING=0
docker images --format "{{.Repository}}:{{.Tag}}" | findstr "xiaozhi-note-backend:latest" >nul
if errorlevel 1 (
    echo [错误] 未找到 xiaozhi-note-backend:latest 镜像
    echo        请先执行: docker load -i xiaozhi-backend-latest.tar
    set MISSING=1
)

docker images --format "{{.Repository}}:{{.Tag}}" | findstr "xiaozhi-note-frontend:latest" >nul
if errorlevel 1 (
    echo [错误] 未找到 xiaozhi-note-frontend:latest 镜像
    echo        请先执行: docker load -i xiaozhi-frontend.tar
    set MISSING=1
)

docker images --format "{{.Repository}}:{{.Tag}}" | findstr "redis:7-alpine" >nul
if errorlevel 1 (
    echo [错误] 未找到 redis:7-alpine 镜像
    echo        请先执行: docker load -i xiaozhi-redis.tar
    set MISSING=1
)

docker images --format "{{.Repository}}:{{.Tag}}" | findstr "mysql:8.0" >nul
if errorlevel 1 (
    echo [错误] 未找到 mysql:8.0 镜像
    echo        请先执行: docker load -i xiaozhi-mysql.tar
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo [提示] 请使用 docker load 导入所有镜像后再运行此脚本
    pause
    exit /b 1
)

echo [2/3] 检查 .env 文件...
if not exist "backend\.env" (
    echo [提示] 未找到 backend\.env 文件，将使用默认配置
    if exist "backend\.env.example" (
        copy "backend\.env.example" "backend\.env" >nul
    )
)

echo [3/3] 启动服务...
echo.

docker-compose -p xiaozhi-note -f docker-compose.quick.yml up -d

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查日志
    pause
    exit /b 1
)

echo.
echo ============================================
echo 启动完成！
echo ============================================
echo.
echo 前端访问地址: http://localhost
echo 后端 API 地址: http://localhost:6789
echo API 文档: http://localhost:6789/docs
echo.
echo 查看日志: docker-compose -p xiaozhi-note -f docker-compose.quick.yml logs -f
echo 停止服务: docker-compose -p xiaozhi-note -f docker-compose.quick.yml down
echo ============================================
echo.
pause
