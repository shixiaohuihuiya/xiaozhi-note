@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================
:: 小智笔记 Docker 快速启动脚本 (Windows)
:: ============================================
:: 使用说明:
:: 1. 确保已执行过 build.bat 构建镜像
:: 2. 双击运行 start.bat 快速启动服务
:: ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║       小智笔记 Docker 快速启动         ║
echo ╚════════════════════════════════════════╝
echo.

:menu
echo 请选择操作:
echo [1] 启动服务
echo [2] 停止服务
echo [3] 重启服务
echo [4] 查看服务状态
echo [5] 查看实时日志
echo [6] 进入后端容器
echo [7] 进入前端容器
echo [8] 备份数据
echo [9] 恢复数据
echo [0] 退出
echo.

set /p choice="请输入选项 (0-9): "

if "%choice%"=="1" goto start_service
if "%choice%"=="2" goto stop_service
if "%choice%"=="3" goto restart_service
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto view_logs
if "%choice%"=="6" goto exec_backend
if "%choice%"=="7" goto exec_frontend
if "%choice%"=="8" goto backup_data
if "%choice%"=="9" goto restore_data
if "%choice%"=="0" goto exit_script
goto invalid_choice

:start_service
echo.
echo ========================================
echo 正在启动服务...
echo ========================================

:: 检查 Docker 是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ Docker 未运行，请先启动 Docker Desktop
    pause
    goto menu
)

:: 检查镜像是否存在
docker-compose config >nul 2>&1
if %errorlevel% neq 0 (
    echo ✗ docker-compose.yml 配置文件错误
    pause
    goto menu
)

docker-compose up -d

if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务启动成功!
    echo.
    echo ================================
    echo 访问地址:
    echo   前端: http://localhost
    echo   后端 API: http://localhost:6789
    echo   Swagger 文档: http://localhost:6789/docs
    echo ================================
    echo.
    
    :: 等待服务就绪
    echo 正在检查服务状态...
    timeout /t 3 /nobreak >nul
    
    docker-compose ps | findstr "Up" >nul
    if %errorlevel% equ 0 (
        echo ✓ 所有服务运行正常
    ) else (
        echo ⚠ 部分服务可能未正常启动，请查看日志
    )
) else (
    echo.
    echo ✗ 服务启动失败
    echo 提示: 检查端口是否被占用或查看日志
)

echo.
pause
goto menu

:stop_service
echo.
echo ========================================
echo 正在停止服务...
echo ========================================

docker-compose stop

if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务已停止
    echo.
) else (
    echo.
    echo ✗ 停止服务失败
)

pause
goto menu

:restart_service
echo.
echo ========================================
echo 正在重启服务...
echo ========================================

docker-compose restart

if %errorlevel% equ 0 (
    echo.
    echo ✓ 服务已重启
    echo.
    echo ================================
    echo 访问地址:
    echo   前端: http://localhost
    echo   后端 API: http://localhost:6789
    echo ================================
    echo.
) else (
    echo.
    echo ✗ 重启服务失败
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
echo ========================================
echo 资源使用情况:
echo ========================================
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" xiaozhi-backend xiaozhi-frontend 2>nul

echo.
pause
goto menu

:view_logs
echo.
echo ========================================
echo 查看实时日志 (按 Ctrl+C 退出)
echo ========================================
echo 选择要查看的服务:
echo [1] 全部服务
echo [2] 后端服务
echo [3] 前端服务
echo.

set /p log_choice="请输入选项 (1-3): "

if "%log_choice%"=="1" docker-compose logs -f --tail=100
if "%log_choice%"=="2" docker-compose logs -f --tail=100 backend
if "%log_choice%"=="3" docker-compose logs -f --tail=100 frontend

goto menu

:exec_backend
echo.
echo ========================================
echo 进入后端容器...
echo ========================================

docker exec -it xiaozhi-backend /bin/bash

if %errorlevel% neq 0 (
    echo ✗ 无法进入容器，请确认服务已启动
)

goto menu

:exec_frontend
echo.
echo ========================================
echo 进入前端容器...
echo ========================================

docker exec -it xiaozhi-frontend /bin/sh

if %errorlevel% neq 0 (
    echo ✗ 无法进入容器，请确认服务已启动
)

goto menu

:backup_data
echo.
echo ========================================
echo 备份数据...
echo ========================================

:: 创建备份目录
if not exist "backups" mkdir backups

:: 生成备份文件名（带时间戳）
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

set "backup_file=backups\xiaozhi_backup_%timestamp%.tar.gz"

echo 正在备份上传文件...
docker run --rm -v %cd%\backend\uploads:/data alpine tar czf /backup.tar.gz -C /data .
if exist "backup.tar.gz" (
    move /y "backup.tar.gz" "%backup_file%" >nul
    echo ✓ 上传文件备份完成: %backup_file%
)

echo.
echo 如需备份数据库，请根据实际使用的数据库类型执行相应命令
echo 例如 MySQL: docker exec xiaozhi-mysql mysqldump -u root -p database_name > backup.sql
echo.

pause
goto menu

:restore_data
echo.
echo ========================================
echo 恢复数据...
echo ========================================

echo 可用的备份文件:
echo.
dir /b backups\*.tar.gz 2>nul
if %errorlevel% neq 0 (
    echo 没有找到备份文件
    pause
    goto menu
)

echo.
set /p backup_file="请输入要恢复的备份文件名: "

if exist "backups\%backup_file%" (
    echo 正在恢复数据...
    docker run --rm -v %cd%\backend\uploads:/data alpine tar xzf /backup.tar.gz -C /data < "backups\%backup_file%"
    
    if %errorlevel% equ 0 (
        echo.
        echo ✓ 数据恢复成功
        echo.
    ) else (
        echo.
        echo ✗ 数据恢复失败
        echo.
    )
) else (
    echo ✗ 备份文件不存在: backups\%backup_file%
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
