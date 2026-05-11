# ====================
# 前端构建阶段
# ====================
FROM node:20-alpine AS builder

WORKDIR /app

# 配置npm使用阿里云镜像
RUN npm config set registry https://registry.npmmirror.com

# 先复制依赖文件，利用缓存层
COPY package.json pnpm-lock.yaml ./

# 安装 pnpm 并安装依赖（使用国内镜像）
RUN npm install -g pnpm --registry=https://registry.npmmirror.com && \
    pnpm install --frozen-lockfile --registry=https://registry.npmmirror.com

# 复制源代码
COPY . .

# 生产构建
RUN pnpm build

# ====================
# 生产运行阶段 (nginx)
# ====================
FROM nginx:alpine

# 复制构建产物到 nginx 目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
