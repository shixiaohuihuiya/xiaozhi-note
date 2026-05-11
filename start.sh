#!/bin/bash

# ============================================
# 小智笔记 Docker 快速启动脚本 (Linux/Mac)
# ============================================
# 使用说明:
# 1. chmod +x start.sh
# 2. ./start.sh
# 3. 确保已执行过 build.sh 构建镜像
# ============================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

print_header() {
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║       小智笔记 Docker 快速启动         ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
}

# 显示菜单
show_menu() {
    clear
    print_header
    echo "请选择操作:"
    echo "  [1] 启动服务"
    echo "  [2] 停止服务"
    echo "  [3] 重启服务"
    echo "  [4] 查看服务状态"
    echo "  [5] 查看实时日志"
    echo "  [6] 进入后端容器"
    echo "  [7] 进入前端容器"
    echo "  [8] 备份数据"
    echo "  [9] 恢复数据"
    echo "  [0] 退出"
    echo ""
}

# 检查 Docker 是否运行
check_docker() {
    if ! docker info &> /dev/null; then
        print_error "Docker 未运行，请先启动 Docker"
        return 1
    fi
    return 0
}

# 启动服务
start_service() {
    echo ""
    print_info "正在启动服务..."
    echo "========================================"
    
    # 检查 Docker
    check_docker || { read -p "按回车键继续..."; return; }
    
    # 检查配置文件
    if ! docker-compose config &> /dev/null; then
        print_error "docker-compose.yml 配置文件错误"
        read -p "按回车键继续..."
        return
    fi
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务启动成功!"
        echo ""
        echo "================================"
        echo "访问地址:"
        echo "  前端: http://localhost"
        echo "  后端 API: http://localhost:6789"
        echo "  Swagger 文档: http://localhost:6789/docs"
        echo "================================"
        echo ""
        
        # 等待服务就绪
        print_info "正在检查服务状态..."
        sleep 3
        
        if docker-compose ps | grep -q "Up"; then
            print_success "所有服务运行正常"
        else
            print_warning "部分服务可能未正常启动，请查看日志"
        fi
    else
        echo ""
        print_error "服务启动失败"
        echo "提示: 检查端口是否被占用或查看日志"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 停止服务
stop_service() {
    echo ""
    print_info "正在停止服务..."
    echo "========================================"
    
    docker-compose stop
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务已停止"
        echo ""
    else
        echo ""
        print_error "停止服务失败"
    fi
    
    read -p "按回车键继续..."
}

# 重启服务
restart_service() {
    echo ""
    print_info "正在重启服务..."
    echo "========================================"
    
    docker-compose restart
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "服务已重启"
        echo ""
        echo "================================"
        echo "访问地址:"
        echo "  前端: http://localhost"
        echo "  后端 API: http://localhost:6789"
        echo "================================"
        echo ""
    else
        echo ""
        print_error "重启服务失败"
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
    print_info "资源使用情况:"
    echo "========================================"
    
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" xiaozhi-backend xiaozhi-frontend 2>/dev/null || \
        print_warning "无法获取资源使用情况（服务可能未启动）"
    
    echo ""
    read -p "按回车键继续..."
}

# 查看日志
view_logs() {
    echo ""
    print_info "查看实时日志 (按 Ctrl+C 退出)"
    echo "========================================"
    echo "选择要查看的服务:"
    echo "  [1] 全部服务"
    echo "  [2] 后端服务"
    echo "  [3] 前端服务"
    echo ""
    
    read -p "请输入选项 (1-3): " log_choice
    
    case $log_choice in
        1) docker-compose logs -f --tail=100 ;;
        2) docker-compose logs -f --tail=100 backend ;;
        3) docker-compose logs -f --tail=100 frontend ;;
        *) print_error "无效选项" ;;
    esac
}

# 进入后端容器
exec_backend() {
    echo ""
    print_info "进入后端容器..."
    echo "========================================"
    
    docker exec -it xiaozhi-backend /bin/bash
    
    if [ $? -ne 0 ]; then
        print_error "无法进入容器，请确认服务已启动"
    fi
}

# 进入前端容器
exec_frontend() {
    echo ""
    print_info "进入前端容器..."
    echo "========================================"
    
    docker exec -it xiaozhi-frontend /bin/sh
    
    if [ $? -ne 0 ]; then
        print_error "无法进入容器，请确认服务已启动"
    fi
}

# 备份数据
backup_data() {
    echo ""
    print_info "备份数据..."
    echo "========================================"
    
    # 创建备份目录
    mkdir -p backups
    
    # 生成备份文件名（带时间戳）
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backups/xiaozhi_backup_${timestamp}.tar.gz"
    
    print_info "正在备份上传文件..."
    
    # 备份 uploads 目录
    if [ -d "backend/uploads" ]; then
        tar czf "$backup_file" -C backend/uploads .
        
        if [ $? -eq 0 ]; then
            print_success "上传文件备份完成: $backup_file"
            
            # 显示文件大小
            file_size=$(du -h "$backup_file" | cut -f1)
            echo "备份文件大小: $file_size"
        else
            print_error "备份失败"
        fi
    else
        print_warning "uploads 目录不存在，跳过备份"
    fi
    
    echo ""
    echo "如需备份数据库，请根据实际使用的数据库类型执行相应命令"
    echo "例如 MySQL: docker exec xiaozhi-mysql mysqldump -u root -p database_name > backup.sql"
    echo ""
    
    read -p "按回车键继续..."
}

# 恢复数据
restore_data() {
    echo ""
    print_info "恢复数据..."
    echo "========================================"
    
    # 查找备份文件
    backup_files=(backups/*.tar.gz)
    
    if [ ${#backup_files[@]} -eq 0 ] || [ ! -e "${backup_files[0]}" ]; then
        print_error "没有找到备份文件"
        read -p "按回车键继续..."
        return
    fi
    
    echo "可用的备份文件:"
    echo ""
    select backup_file in "${backup_files[@]}"; do
        if [ -n "$backup_file" ]; then
            break
        else
            print_error "无效选择"
        fi
    done
    
    echo ""
    read -p "确认恢复此备份? (y/n): " confirm
    
    if [[ "$confirm" =~ ^[Yy]$ ]]; then
        print_info "正在恢复数据..."
        
        # 创建临时目录
        temp_dir=$(mktemp -d)
        tar xzf "$backup_file" -C "$temp_dir"
        
        if [ $? -eq 0 ]; then
            # 恢复文件到 uploads 目录
            mkdir -p backend/uploads
            cp -r "$temp_dir"/* backend/uploads/
            
            # 清理临时目录
            rm -rf "$temp_dir"
            
            print_success "数据恢复成功"
            echo ""
        else
            print_error "数据恢复失败"
            rm -rf "$temp_dir"
        fi
    else
        print_info "已取消恢复操作"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 主循环
while true; do
    show_menu
    read -p "请输入选项 (0-9): " choice
    
    case $choice in
        1) start_service ;;
        2) stop_service ;;
        3) restart_service ;;
        4) check_status ;;
        5) view_logs ;;
        6) exec_backend ;;
        7) exec_frontend ;;
        8) backup_data ;;
        9) restore_data ;;
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
