#!/bin/bash

# ============================================
# 小智笔记 Docker 快速打包脚本 (Linux/Mac)
# ============================================
# 使用说明:
# 1. chmod +x build.sh
# 2. ./build.sh
# 3. 根据提示选择操作
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示菜单
show_menu() {
    clear
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║       小智笔记 Docker 打包工具         ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "请选择操作:"
    echo "  [1] 构建镜像并启动服务"
    echo "  [2] 仅构建镜像 (不启动)"
    echo "  [3] 启动服务"
    echo "  [4] 停止服务"
    echo "  [5] 重启服务"
    echo "  [6] 查看服务状态"
    echo "  [7] 查看日志"
    echo "  [8] 停止并删除容器、镜像、网络"
    echo "  [9] 拉取最新代码并重新部署"
    echo "  [0] 退出"
    echo ""
}

# 构建并启动
build_and_start() {
    echo ""
    print_info "开始构建镜像并启动服务..."
    echo "========================================"
    
    docker-compose down
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "构建和启动成功!"
        echo ""
        echo "前端访问地址: http://localhost"
        echo "后端 API 地址: http://localhost:6789"
        echo ""
    else
        echo ""
        print_error "构建或启动失败，请检查错误信息"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 仅构建
build_only() {
    echo ""
    print_info "开始构建镜像..."
    echo "========================================"
    
    docker-compose build
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "镜像构建成功!"
        echo ""
    else
        echo ""
        print_error "镜像构建失败，请检查错误信息"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 启动服务
start_service() {
    echo ""
    print_info "启动服务..."
    echo "========================================"
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务启动成功!"
        echo ""
        echo "前端访问地址: http://localhost"
        echo "后端 API 地址: http://localhost:6789"
        echo ""
    else
        echo ""
        print_error "服务启动失败，请检查错误信息"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 停止服务
stop_service() {
    echo ""
    print_info "停止服务..."
    echo "========================================"
    
    docker-compose stop
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务已停止"
        echo ""
    else
        echo ""
        print_error "停止服务失败"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 重启服务
restart_service() {
    echo ""
    print_info "重启服务..."
    echo "========================================"
    
    docker-compose restart
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务已重启"
        echo ""
    else
        echo ""
        print_error "重启服务失败"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 查看状态
check_status() {
    echo ""
    print_info "服务状态:"
    echo "========================================"
    
    docker-compose ps
    
    echo ""
    read -p "按回车键继续..."
}

# 查看日志
view_logs() {
    echo ""
    print_info "查看日志 (按 Ctrl+C 退出)"
    echo "========================================"
    echo "选择要查看的服务:"
    echo "  [1] 全部服务"
    echo "  [2] 后端服务"
    echo "  [3] 前端服务"
    echo ""
    
    read -p "请输入选项 (1-3): " log_choice
    
    case $log_choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs -f backend ;;
        3) docker-compose logs -f frontend ;;
        *) print_error "无效选项" ;;
    esac
}

# 清理所有
clean_all() {
    echo ""
    print_warning "⚠️  警告: 此操作将删除所有容器、镜像和网络"
    echo "========================================"
    
    read -p "确认执行? (y/n): " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        echo ""
        print_info "正在清理..."
        
        docker-compose down -v --rmi all --remove-orphans
        
        if [ $? -eq 0 ]; then
            echo ""
            print_success "清理完成"
            echo ""
        else
            echo ""
            print_error "清理失败"
            echo ""
        fi
    else
        echo ""
        print_info "已取消操作"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 拉取并部署
pull_and_deploy() {
    echo ""
    print_info "拉取最新代码并重新部署..."
    echo "========================================"
    
    # 检查 git 是否可用
    if ! command -v git &> /dev/null; then
        print_error "Git 未安装或未添加到环境变量"
        read -p "按回车键继续..."
        return
    fi
    
    print_info "正在拉取最新代码..."
    git pull
    
    if [ $? -ne 0 ]; then
        print_error "代码拉取失败"
        read -p "按回车键继续..."
        return
    fi
    
    echo ""
    print_info "正在重新构建和部署..."
    
    docker-compose down
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "部署成功!"
        echo ""
        echo "前端访问地址: http://localhost"
        echo "后端 API 地址: http://localhost:6789"
        echo ""
    else
        echo ""
        print_error "部署失败，请检查错误信息"
        echo ""
    fi
    
    read -p "按回车键继续..."
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-9): " choice
    
    case $choice in
        1) build_and_start ;;
        2) build_only ;;
        3) start_service ;;
        4) stop_service ;;
        5) restart_service ;;
        6) check_status ;;
        7) view_logs ;;
        8) clean_all ;;
        9) pull_and_deploy ;;
        0) 
            echo ""
            print_info "感谢使用，再见!"
            echo ""
            exit 0
            ;;
        *) 
            echo ""
            print_error "无效选项，请重新输入"
            echo ""
            read -p "按回车键继续..."
            ;;
    esac
done
