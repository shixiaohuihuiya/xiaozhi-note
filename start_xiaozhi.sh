#!/bin/bash
# ============================================
# 小智笔记 - 快速启动（使用已导入的镜像）- Linux版本
# ============================================

echo "============================================"
echo "小智笔记 - 快速启动（使用已导入的镜像）"
echo "============================================"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo "[错误] Docker 未运行，请先启动 Docker"
    exit 1
fi

echo "[1/3] 检查镜像..."
echo ""

# 检查必需的镜像
MISSING=0

if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "xiaozhi-note-backend:latest"; then
    echo "[错误] 未找到 xiaozhi-note-backend:latest 镜像"
    echo "       请先执行: docker load -i xiaozhi-backend-latest.tar"
    MISSING=1
fi

if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "xiaozhi-note-frontend:latest"; then
    echo "[错误] 未找到 xiaozhi-note-frontend:latest 镜像"
    echo "       请先执行: docker load -i xiaozhi-frontend.tar"
    MISSING=1
fi

if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "redis:7-alpine"; then
    echo "[错误] 未找到 redis:7-alpine 镜像"
    echo "       请先执行: docker load -i xiaozhi-redis.tar"
    MISSING=1
fi

if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "mysql:8.0"; then
    echo "[错误] 未找到 mysql:8.0 镜像"
    echo "       请先执行: docker load -i xiaozhi-mysql.tar"
    MISSING=1
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo "[提示] 请使用 docker load 导入所有镜像后再运行此脚本"
    exit 1
fi

echo "[2/3] 检查 .env 文件..."
if [ ! -f "backend/.env" ]; then
    echo "[提示] 未找到 backend/.env 文件，将使用默认配置"
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
    fi
fi

echo "[3/3] 启动服务..."
echo ""

# 检测 Docker Compose 版本并设置项目名
COMPOSE_VERSION=$(docker-compose version --short 2>/dev/null || echo "1")
if [[ "$COMPOSE_VERSION" == v2* ]] || [[ "$COMPOSE_VERSION" == 2.* ]]; then
    # Docker Compose v2.x - 支持 name 指令
    docker-compose -f docker-compose.quick.yml up -d
else
    # Docker Compose v1.x - 需要使用 -p 参数
    docker-compose -p xiaozhi-note -f docker-compose.quick.yml up -d
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] 启动失败，请检查日志"
    exit 1
fi

echo ""
echo "============================================"
echo "启动完成！"
echo "============================================"
echo ""
echo "前端访问地址: http://localhost"
echo "后端 API 地址: http://localhost:6789"
echo "API 文档: http://localhost:6789/docs"
echo ""
echo "查看日志: docker-compose -f docker-compose.quick.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.quick.yml down"
echo "============================================"
echo ""
