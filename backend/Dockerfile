# ====================
# 后端构建阶段
# ====================
FROM python:3.11-slim AS builder

WORKDIR /app

# 安装编译依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

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

# 创建上传目录
RUN mkdir -p /app/uploads

# 复制应用代码
COPY app/ ./app/
COPY run.py .

# 暴露端口
EXPOSE 6789

# 启动命令
CMD ["python", "run.py"]
