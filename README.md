# 📝 小智笔记 (Xiaozhi Note)

一个简洁、美观的现代化笔记管理平台，支持Markdown编辑、AI辅助写作、多用户管理等功能。

---

## ✨ 功能特性

###  核心功能

- **Markdown 笔记编辑**
  - 支持 Markdown 语法编辑
  - 实时预览（分屏/编辑/预览模式）
  - 代码块高亮显示
  - 快速插入格式工具栏（粗体、斜体、标题、列表、代码块等）

- **AI 智能助手** 🤖
  - AI 续写功能
  - 内容润色与扩写
  - 智能对话辅助写作
  - 对话历史保存

- **文章管理**
  - 文章发布与审核流程
  - 分类与标签管理
  - 文章搜索与筛选
  - 软删除机制（支持恢复）

- **用户系统**
  - 用户注册与登录
  - JWT 认证机制
  - 角色权限管理（普通用户/管理员/超级管理员）
  - 个人资料管理
  - 密码修改

- **互动功能**
  - 文章点赞
  - 评论系统（支持回复）
  - 浏览量统计
  - 通知系统

- **后台管理** ️
  - 仪表板数据统计
  - 用户管理（导入/导出）
  - 文章管理（审核/删除）
  - 分类/标签管理
  - 评论管理
  - 图片管理
  - 留言墙管理
  - 站点配置
  - AI 配置管理

- **响应式设计** 📱
  - 完美支持移动端
  - 暗色/亮色主题切换
  - 多主题色支持（7种颜色方案）

---

## ️ 技术栈

### 前端 (Frontend)
- **框架**: Vue 3 + Vite
- **UI 库**: Ant Design Vue
- **状态管理**: Pinia
- **Markdown 渲染**: MarkdownIt
- **代码高亮**: Highlight.js
- **样式**: Less
- **包管理**: pnpm

### 后端 (Backend)
- **框架**: FastAPI (Python)
- **数据库**: MySQL 8.0
- **ORM**: SQLAlchemy (Async)
- **缓存**: Redis 7
- **认证**: JWT (python-jose)
- **密码哈希**: Bcrypt
- **验证码**: Captcha

### 部署 (Deployment)
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **多阶段构建**: 优化镜像体积

---

## 🚀 快速启动

### 前置要求

- Docker & Docker Compose
- Git

### 安装步骤

#### 1. 克隆项目

```bash

**gitee**
git clone https://github.com/xhh_code/xiaozhi-note.git
**github**
git clone https://github.com/shixiaohuihuiya/xiaozhi-note.git

cd xiaozhi-note
```

#### 2. 配置环境变量

```bash
# 复制环境配置文件
cp backend/.env.example backend/.env

# 编辑配置文件
# 修改数据库密码、JWT密钥等敏感信息
nano backend/.env
```

**必须配置的关键参数**:
```env
# 数据库配置
DB_HOST=xiaozhi-mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_secure_password
DB_NAME=xiaozhi_notes

# Redis 配置
REDIS_URL=redis://:your_redis_password@xiaozhi-redis:6379/0

# JWT 配置
JWT_SECRET_KEY=your_super_secret_key_change_this
JWT_REFRESH_SECRET_KEY=your_refresh_secret_key_change_this

# AI 配置（可选）
AI_API_KEY=your_doubao_api_key
```

#### 3. 启动服务

```bash
# 使用 Docker Compose 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 4. 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:6789
- **默认管理员账号**: 
  - 用户名: `superadmin`
  - 密码: `admin123456`

---

## 📂 项目结构

```
xiaozhi-note/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── article.py     # 文章模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── category.py    # 分类模型
│   │   │   ├── tag.py         # 标签模型
│   │   │   ├── comment.py     # 评论模型
│   │   │   ├── notification.py # 通知模型
│   │   │   └── ...
│   │   ├── routers/           # API 路由
│   │   │   ├── article.py     # 文章接口
│   │   │   ├── auth.py        # 认证接口
│   │   │   ├── admin.py       # 管理接口
│   │   │   ├── ai.py          # AI 接口
│   │   │   └── ...
│   │   ├── schemas/           # 数据验证
│   │   ├── services/          # 业务逻辑
│   │   ├── utils/             # 工具函数
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   └── main.py            # 应用入口
│   ├── requirements.txt       # Python 依赖
│   ├── Dockerfile
│   └── .env.example           # 环境变量示例
│
├── frontend/                   # 前端服务
│   ├── src/
│   │   ├── api/               # API 调用
│   │   ├── components/        # 公共组件
│   │   ├── layouts/           # 布局组件
│   │   ├── views/             # 页面视图
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── router/            # 路由配置
│   │   ├── utils/             # 工具函数
│   │   └── styles/            # 全局样式
│   ├── package.json
│   ├── vite.config.js
│   ├── Dockerfile
│   └── nginx.conf             # Nginx 配置
│
── docs/                       # 项目文档
│   ├── 接口文档.md
│   ├── 数据库设计.md
│   ├── 需求文档.md
│   └── ...
│
── docker-compose.yml          # Docker 编排配置
├── .gitignore
── README.md
```

---

##  开发模式

### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器（热重载）
pnpm dev

# 构建生产版本
pnpm build

# 预览生产版本
pnpm preview
```

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python run.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --port 6789
```

---

## 📖 API 文档

### 主要接口

| 接口 | 方法 | 描述 | 认证 |
|------|------|------|------|
| `/auth/login` | POST | 用户登录 |  |
| `/auth/register` | POST | 用户注册 | ❌ |
| `/articles` | GET | 获取文章列表 |  |
| `/articles/{slug}` | GET | 获取文章详情 | ❌ |
| `/articles` | POST | 创建文章 | ✅ |
| `/articles/{id}` | PUT | 更新文章 | ✅ |
| `/articles/{id}` | DELETE | 删除文章 | ✅ |
| `/comments` | POST | 发表评论 | ✅ |
| `/like/articles/{id}` | POST | 点赞文章 | ✅ |
| `/notifications` | GET | 获取通知 | ✅ |
| `/admin/articles` | GET | 管理文章（管理员） | ✅ 🔐 |
| `/admin/users` | GET | 管理用户（管理员） | ✅  |

> 🔐 表示需要管理员权限

详细的接口文档请参考 [docs/接口文档.md](docs/接口文档.md)

---

## 🗄️ 数据库设计

主要数据表:

- **users** - 用户表
- **articles** - 文章表
- **categories** - 分类表
- **tags** - 标签表
- **article_tags** - 文章标签关联表
- **comments** - 评论表
- **likes** - 点赞表
- **notifications** - 通知表
- **messages** - 站内消息表
- **site_configs** - 站点配置表
- **uploads** - 上传记录表

详细设计请参考 [docs/数据库设计.md](docs/数据库设计.md)

---

## 🎨 主题定制

项目支持多种主题色和暗色模式：

### 主题色
- 默认蓝 `#1890ff`
- 清新绿 `#52c41a`
- 活力橙 `#faad14`
- 热情红 `#f5222d`
- 优雅紫 `#722ed1`
- 天空蓝 `#13c2c2`
- 樱花粉 `#eb2f96`

### 暗色模式
通过点击右上角的月亮/太阳图标切换暗色/亮色模式。

---

## 🔐 安全特性

- JWT 令牌认证机制
- 密码 Bcrypt 加密存储
- 图片上传验证
- 频率限制（Redis）
- CORS 跨域配置
- 输入数据验证（Pydantic）
- SQL 注入防护（SQLAlchemy）

---

## 🐳 Docker 部署优化

### 镜像优化
- 使用多阶段构建
- 阿里云镜像加速
- 精简运行依赖
- 前端镜像 ~100MB
- 后端镜像 ~200MB

### 数据持久化
- MySQL 数据: `mysql-data` volume
- Redis 数据: `redis-data` volume
- 上传文件: `uploads/` 目录挂载

---

## 📝 注意事项

1. **首次启动**: 系统会自动创建超级管理员账号
2. **数据库初始化**: 容器首次启动时会自动创建数据库和表
3. **静态资源**: 上传的图片保存在 `backend/uploads/` 目录
4. **环境变量**: 生产环境请务必修改 `.env` 中的密钥
5. **防火墙**: 确保 80 端口（前端）和 6789 端口（后端）已开放

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

本项目仅供学习和参考使用。

---

## 📞 联系方式

如有问题，欢迎通过以下方式联系：

- 提交 Issue
<<<<<<< HEAD
- 发送邮件至: support@example.com
=======
- 发送邮件至: 2295465016@qq.com
>>>>>>> master

---

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

**Happy Coding! 🎉**
