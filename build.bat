@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
:: 小智笔记 Docker 快速打包脚本 (Windows)
:: ============================================
:: 使用说明:
:: 1. 双击运行 build.bat
:: 2. 根据提示选择操作
:: ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║       小智笔记 Docker 打包工具         ║
echo ╚════════════════════════════════════════╝
echo.

:menu
echo 请选择操作:
echo [1] 构建镜像并启动服务
echo [2] 仅构建镜像 (不启动)
echo [3] 启动服务
echo [4] 停止服务
echo [5] 重启服务
echo [6] 查看服务状态
echo [7] 查看日志
echo [8] 停止并删除容器、镜像、网络
echo [9] 拉取最新代码并重新部署
echo [0] 退出
echo.

set /p choice="请输入选项 (0-9): "

if "%choice%"=="1" goto build_and_start
if "%choice%"=="2" goto build_only
if "%choice%"=="3" goto start_service
if "%choice%"=="4" goto stop_service
if "%choice%"=="5" goto restart_service
if "%choice%"=="6" goto check_status
if "%choice%"=="7" goto view_logs
if "%choice%"=="8" goto clean_all
if "%choice%"=="9" goto pull_and_deploy
if "%choice%"=="0" goto exit_script
goto invalid_choice

:build_and_start
echo.
echo ========================================
echo 开始构建镜像并启动服务...
echo ========================================
docker-compose down
docker-compose up -d --build
if %errorlevel% equ 0 (
    echo.
    echo ✓ 构建和启动成功!
    echo.
    echo 前端访问地址: http://localhost
    echo 后端 API 地址: http://localhost:6789
    echo.
) else (
    echo.
    echo ✗ 构建或启动失败，请检查错误信息
    echo.
)
pause
goto menu

:build_only
echo.
echo ========================================
echo 开始构建镜像...
echo ========================================
docker-compose build
if %errorlevel% equ 0 (
    echo.
    echo ✓ 镜像构建成功!
    echo.
) else (
    echo.
    echo ✗ 镜像构建失败，请检查错误信息
    echo.
)
pause
goto menu

:start_service
echo.
echo ========================================
echo 启动服务...
echo ========================================
docker-compose up -d
if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务启动成功!
    echo.
    echo 前端访问地址: http://localhost
    echo 后端 API 地址: http://localhost:6789
    echo.
) else (
    echo.
    echo ✗ 服务启动失败，请检查错误信息
    echo.
)
pause
goto menu

:stop_service
echo.
echo ========================================
echo 停止服务...
echo ========================================
docker-compose stop
if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务已停止
    echo.
) else (
    echo.
    echo ✗ 停止服务失败
    echo.
)
pause
goto menu

:restart_service
echo.
echo ========================================
echo 重启服务...
echo ========================================
docker-compose restart
if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务已重启
    echo.
) else (
    echo.
    echo ✗ 重启服务失败
    echo.
)
pause
goto menu

:check_status
echo.
echo ========================================
echo 服务状态:
echo ========================================
docker-compose ps
echo.
pause
goto menu

:view_logs
echo.
echo ========================================
echo 查看日志 (按 Ctrl+C 退出)
echo ========================================
echo 选择要查看的服务:
echo [1] 全部服务
echo [2] 后端服务
echo [3] 前端服务
echo.

set /p log_choice="请输入选项 (1-3): "

if "%log_choice%"=="1" docker-compose logs -f
if "%log_choice%"=="2" docker-compose logs -f backend
if "%log_choice%"=="3" docker-compose logs -f frontend

goto menu

:clean_all
echo.
echo ========================================
echo ⚠️  警告: 此操作将删除所有容器、镜像和网络
echo ========================================
set /p confirm="确认执行? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo 正在清理...
    docker-compose down -v --rmi all --remove-orphans
    if %errorlevel% equ 0 (
        echo.
        echo ✓ 清理完成
        echo.
    ) else (
        echo.
        echo ✗ 清理失败
        echo.
    )
) else (
    echo.
    echo 已取消操作
    echo.
)
pause
goto menu

:pull_and_deploy
echo.
echo ========================================
echo 拉取最新代码并重新部署...
echo ========================================

:: Check if git is available
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ✗ Git 未安装或未添加到环境变量
    pause
    goto menu
)

echo 正在拉取最新代码...
git pull
if %errorlevel% neq 0 (
    echo ✗ 代码拉取失败
    pause
    goto menu
)

echo.
echo 正在重新构建和部署...
docker-compose down
docker-compose up -d --build
if %errorlevel% equ 0 (
    echo.
    echo ✓ 部署成功!
    echo.
    echo 前端访问地址: http://localhost
    echo 后端 API 地址: http://localhost:6789
    echo.
) else (
    echo.
    echo ✗ 部署失败，请检查错误信息
    echo.
)
pause
goto menu

:invalid_choice
echo.
echo ✗ 无效选项，请重新输入
echo.
goto menu

:exit_script
echo.
echo 感谢使用，再见!
echo.
exit /b 0
