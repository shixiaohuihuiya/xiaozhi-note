#!/bin/bash

# ============================================
# Nginx 代理配置快速重置脚本 (Linux)
# ============================================
# 使用说明:
# 1. chmod +x reset-nginx.sh
# 2. sudo ./reset-nginx.sh (需要 root 权限)
# 3. 根据提示选择配置类型并填写参数
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

# 检查 root 权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "此脚本需要 root 权限运行"
        echo "请使用: sudo $0"
        exit 1
    fi
}

# 查找 nginx 配置文件目录
find_nginx_conf_dir() {
    local possible_dirs=(
        "/etc/nginx/conf.d"
        "/etc/nginx/sites-enabled"
        "/usr/local/etc/nginx/conf.d"
        "/opt/nginx/conf/conf.d"
    )
    
    for dir in "${possible_dirs[@]}"; do
        if [ -d "$dir" ]; then
            echo "$dir"
            return 0
        fi
    done
    
    print_error "未找到 nginx 配置目录"
    echo "常见位置:"
    echo "  - /etc/nginx/conf.d"
    echo "  - /etc/nginx/sites-enabled"
    echo "  - /usr/local/etc/nginx/conf.d"
    return 1
}

# 显示菜单
show_menu() {
    clear
    echo ""
    echo "╔════════════════════════════════════════╗"
    echo "║     Nginx 代理配置快速重置工具         ║"
    echo "╚════════════════════════════════════════╝"
    echo ""
    echo "请选择配置类型:"
    echo "  [1] HTTP 配置 (无 SSL)"
    echo "  [2] HTTPS 配置 (带 SSL)"
    echo "  [3] 查看当前配置"
    echo "  [4] 备份当前配置"
    echo "  [5] 恢复备份配置"
    echo "  [6] 测试 nginx 配置"
    echo "  [7] 重启 nginx 服务"
    echo "  [0] 退出"
    echo ""
}

# 应用 HTTP 配置
apply_http_config() {
    echo ""
    print_info "配置 HTTP 代理..."
    echo "========================================"
    
    # 获取参数
    read -p "请输入域名 (如: example.com): " domain
    read -p "请输入后端地址 (如: localhost:6789): " backend_host
    read -p "请输入前端根目录 (如: /usr/share/nginx/html): " frontend_root
    
    if [ -z "$domain" ] || [ -z "$backend_host" ] || [ -z "$frontend_root" ]; then
        print_error "所有参数都必须填写"
        read -p "按回车键继续..."
        return
    fi
    
    # 查找配置目录
    conf_dir=$(find_nginx_conf_dir)
    if [ $? -ne 0 ]; then
        read -p "按回车键继续..."
        return
    fi
    
    print_info "配置目录: $conf_dir"
    
    # 生成配置文件名
    config_file="$conf_dir/xiaozhi-note.conf"
    
    # 备份现有配置
    if [ -f "$config_file" ]; then
        backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$config_file" "$backup_file"
        print_info "已备份现有配置: $backup_file"
    fi
    
    # 从模板生成配置
    template_file="$(dirname "$0")/nginx/http.conf"
    if [ ! -f "$template_file" ]; then
        # 尝试其他路径
        template_file="./nginx/http.conf"
        if [ ! -f "$template_file" ]; then
            template_file="../nginx/http.conf"
        fi
    fi
    
    if [ ! -f "$template_file" ]; then
        print_error "未找到 HTTP 配置模板文件"
        read -p "按回车键继续..."
        return
    fi
    
    # 替换模板变量
    sed -e "s|{{DOMAIN}}|$domain|g" \
        -e "s|{{BACKEND_HOST}}|$backend_host|g" \
        -e "s|{{FRONTEND_ROOT}}|$frontend_root|g" \
        "$template_file" > "$config_file"
    
    if [ $? -eq 0 ]; then
        print_success "HTTP 配置已生成: $config_file"
        
        # 测试配置
        print_info "测试 nginx 配置..."
        nginx -t
        
        if [ $? -eq 0 ]; then
            print_success "配置测试通过"
            
            # 询问是否重启
            read -p "是否立即重启 nginx? (y/n): " restart_choice
            if [[ "$restart_choice" =~ ^[Yy]$ ]]; then
                systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null
                
                if [ $? -eq 0 ]; then
                    print_success "Nginx 已重启"
                    echo ""
                    echo "================================"
                    echo "访问地址: http://$domain"
                    echo "================================"
                else
                    print_error "重启 nginx 失败"
                fi
            fi
        else
            print_error "配置测试失败，请检查配置"
            echo "已保留配置文件，修复后手动执行: nginx -t && systemctl restart nginx"
        fi
    else
        print_error "生成配置文件失败"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 应用 HTTPS 配置
apply_https_config() {
    echo ""
    print_info "配置 HTTPS 代理..."
    echo "========================================"
    
    # 获取参数
    read -p "请输入域名 (如: example.com): " domain
    read -p "请输入后端地址 (如: localhost:6789): " backend_host
    read -p "请输入前端根目录 (如: /usr/share/nginx/html): " frontend_root
    read -p "请输入 SSL 证书路径 (如: /etc/nginx/ssl/cert.pem): " ssl_cert
    read -p "请输入 SSL 私钥路径 (如: /etc/nginx/ssl/key.pem): " ssl_key
    
    if [ -z "$domain" ] || [ -z "$backend_host" ] || [ -z "$frontend_root" ] || [ -z "$ssl_cert" ] || [ -z "$ssl_key" ]; then
        print_error "所有参数都必须填写"
        read -p "按回车键继续..."
        return
    fi
    
    # 验证证书文件是否存在
    if [ ! -f "$ssl_cert" ]; then
        print_warning "SSL 证书文件不存在: $ssl_cert"
        read -p "是否继续? (y/n): " continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    if [ ! -f "$ssl_key" ]; then
        print_warning "SSL 私钥文件不存在: $ssl_key"
        read -p "是否继续? (y/n): " continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    # 查找配置目录
    conf_dir=$(find_nginx_conf_dir)
    if [ $? -ne 0 ]; then
        read -p "按回车键继续..."
        return
    fi
    
    print_info "配置目录: $conf_dir"
    
    # 生成配置文件名
    config_file="$conf_dir/xiaozhi-note.conf"
    
    # 备份现有配置
    if [ -f "$config_file" ]; then
        backup_file="${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$config_file" "$backup_file"
        print_info "已备份现有配置: $backup_file"
    fi
    
    # 从模板生成配置
    template_file="$(dirname "$0")/nginx/https.conf"
    if [ ! -f "$template_file" ]; then
        # 尝试其他路径
        template_file="./nginx/https.conf"
        if [ ! -f "$template_file" ]; then
            template_file="../nginx/https.conf"
        fi
    fi
    
    if [ ! -f "$template_file" ]; then
        print_error "未找到 HTTPS 配置模板文件"
        read -p "按回车键继续..."
        return
    fi
    
    # 替换模板变量
    sed -e "s|{{DOMAIN}}|$domain|g" \
        -e "s|{{BACKEND_HOST}}|$backend_host|g" \
        -e "s|{{FRONTEND_ROOT}}|$frontend_root|g" \
        -e "s|{{SSL_CERT_PATH}}|$ssl_cert|g" \
        -e "s|{{SSL_KEY_PATH}}|$ssl_key|g" \
        "$template_file" > "$config_file"
    
    if [ $? -eq 0 ]; then
        print_success "HTTPS 配置已生成: $config_file"
        
        # 测试配置
        print_info "测试 nginx 配置..."
        nginx -t
        
        if [ $? -eq 0 ]; then
            print_success "配置测试通过"
            
            # 询问是否重启
            read -p "是否立即重启 nginx? (y/n): " restart_choice
            if [[ "$restart_choice" =~ ^[Yy]$ ]]; then
                systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null
                
                if [ $? -eq 0 ]; then
                    print_success "Nginx 已重启"
                    echo ""
                    echo "================================"
                    echo "访问地址: https://$domain"
                    echo "================================"
                else
                    print_error "重启 nginx 失败"
                fi
            fi
        else
            print_error "配置测试失败，请检查配置"
            echo "已保留配置文件，修复后手动执行: nginx -t && systemctl restart nginx"
        fi
    else
        print_error "生成配置文件失败"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 查看当前配置
view_current_config() {
    echo ""
    print_info "当前 Nginx 配置:"
    echo "========================================"
    
    conf_dir=$(find_nginx_conf_dir)
    if [ $? -ne 0 ]; then
        read -p "按回车键继续..."
        return
    fi
    
    config_file="$conf_dir/xiaozhi-note.conf"
    
    if [ -f "$config_file" ]; then
        echo ""
        cat "$config_file"
        echo ""
    else
        print_warning "未找到小智笔记的 nginx 配置文件"
        echo "可能的配置目录: $conf_dir"
        echo ""
        ls -la "$conf_dir" 2>/dev/null | grep -E "\.conf$"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 备份配置
backup_config() {
    echo ""
    print_info "备份 Nginx 配置..."
    echo "========================================"
    
    conf_dir=$(find_nginx_conf_dir)
    if [ $? -ne 0 ]; then
        read -p "按回车键继续..."
        return
    fi
    
    # 创建备份目录
    backup_base_dir="/var/backups/nginx"
    mkdir -p "$backup_base_dir"
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="$backup_base_dir/nginx-config-${timestamp}.tar.gz"
    
    tar czf "$backup_file" -C "$(dirname "$conf_dir")" "$(basename "$conf_dir")"
    
    if [ $? -eq 0 ]; then
        print_success "配置备份完成: $backup_file"
        
        # 显示备份文件大小
        file_size=$(du -h "$backup_file" | cut -f1)
        echo "备份文件大小: $file_size"
        
        # 列出所有备份
        echo ""
        print_info "现有备份:"
        ls -lh "$backup_base_dir"/nginx-config-*.tar.gz 2>/dev/null | tail -5
    else
        print_error "备份失败"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 恢复配置
restore_config() {
    echo ""
    print_info "恢复 Nginx 配置..."
    echo "========================================"
    
    backup_base_dir="/var/backups/nginx"
    
    if [ ! -d "$backup_base_dir" ]; then
        print_error "备份目录不存在: $backup_base_dir"
        read -p "按回车键继续..."
        return
    fi
    
    # 查找备份文件
    backup_files=("$backup_base_dir"/nginx-config-*.tar.gz)
    
    if [ ${#backup_files[@]} -eq 0 ] || [ ! -e "${backup_files[0]}" ]; then
        print_error "没有找到备份文件"
        read -p "按回车键继续..."
        return
    fi
    
    echo "可用的备份文件:"
    echo ""
    
    # 显示备份列表
    i=1
    declare -a file_list
    for file in "${backup_files[@]}"; do
        filename=$(basename "$file")
        filesize=$(du -h "$file" | cut -f1)
        echo "  [$i] $filename ($filesize)"
        file_list+=("$file")
        ((i++))
    done
    
    echo ""
    read -p "请选择要恢复的备份编号: " choice
    
    if [ "$choice" -ge 1 ] && [ "$choice" -le ${#file_list[@]} ]; then
        selected_file="${file_list[$((choice-1))]}"
        
        echo ""
        read -p "确认恢复此备份? (y/n): " confirm
        
        if [[ "$confirm" =~ ^[Yy]$ ]]; then
            print_info "正在恢复配置..."
            
            # 先备份当前配置
            conf_dir=$(find_nginx_conf_dir)
            if [ $? -eq 0 ]; then
                current_backup="${conf_dir}/pre-restore-backup.$(date +%Y%m%d_%H%M%S)"
                cp -r "$conf_dir" "$current_backup" 2>/dev/null
                print_info "已备份当前配置: $current_backup"
            fi
            
            # 恢复备份
            tar xzf "$selected_file" -C /
            
            if [ $? -eq 0 ]; then
                print_success "配置恢复成功"
                
                # 测试配置
                print_info "测试 nginx 配置..."
                nginx -t
                
                if [ $? -eq 0 ]; then
                    print_success "配置测试通过"
                    
                    read -p "是否立即重启 nginx? (y/n): " restart_choice
                    if [[ "$restart_choice" =~ ^[Yy]$ ]]; then
                        systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null
                        
                        if [ $? -eq 0 ]; then
                            print_success "Nginx 已重启"
                        else
                            print_error "重启 nginx 失败"
                        fi
                    fi
                else
                    print_error "配置测试失败，正在回滚..."
                    if [ -d "$current_backup" ]; then
                        cp -r "$current_backup"/* "$conf_dir"/
                        print_success "已回滚到恢复前的配置"
                    fi
                fi
            else
                print_error "恢复失败"
            fi
        else
            print_info "已取消恢复操作"
        fi
    else
        print_error "无效选择"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 测试配置
test_config() {
    echo ""
    print_info "测试 Nginx 配置..."
    echo "========================================"
    
    nginx -t
    
    if [ $? -eq 0 ]; then
        print_success "配置测试通过"
    else
        print_error "配置测试失败，请检查错误信息"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 重启 nginx
restart_nginx() {
    echo ""
    print_info "重启 Nginx 服务..."
    echo "========================================"
    
    systemctl restart nginx 2>/dev/null || service nginx restart 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Nginx 已重启"
        
        # 检查状态
        sleep 1
        if systemctl is-active --quiet nginx 2>/dev/null || service nginx status 2>/dev/null | grep -q "running"; then
            print_success "Nginx 运行正常"
        else
            print_warning "Nginx 可能未正常运行，请检查日志"
        fi
    else
        print_error "重启 nginx 失败"
    fi
    
    echo ""
    read -p "按回车键继续..."
}

# 主循环
check_root

while true; do
    show_menu
    read -p "请输入选项 (0-7): " choice
    
    case $choice in
        1) apply_http_config ;;
        2) apply_https_config ;;
        3) view_current_config ;;
        4) backup_config ;;
        5) restore_config ;;
        6) test_config ;;
        7) restart_nginx ;;
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
