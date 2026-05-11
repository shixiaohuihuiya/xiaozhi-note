# ====================
# 后端构建阶段
# ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# 配置阿里云镜像源加速
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 配置pip使用阿里云镜像
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 安装依赖到虚拟环境
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ====================
# 生产运行阶段
# ====================
FROM python:3.11-slim

WORKDIR /app

# 复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 激活虚拟环境
ENV PATH="/opt/venv/bin:$PATH"

# 安装字体（用于验证码生成）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends fonts-dejavu-core fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# 创建上传和模板目录
RUN mkdir -p /app/uploads /app/templates

# 复制应用代码
COPY app/ ./app/
COPY templates/ ./templates/
COPY run.py .

# 暴露端口
EXPOSE 6789

# 启动命令 - 使用run.py启动
CMD ["python", "run.py"]
