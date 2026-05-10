<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-container">
        <div class="hero-content">
          <h1 class="hero-title">小智笔记</h1>
          <p class="hero-subtitle">智能写作助手，让创作更轻松</p>
          <p class="hero-desc">支持 Markdown 编辑、AI 智能辅助、多主题切换，打造沉浸式写作体验</p>
          <div class="hero-actions">
            <a-button type="primary" size="large" class="btn-primary" @click="$router.push('/articles')">
              浏览笔记
            </a-button>
            <a-button size="large" class="btn-secondary" @click="$router.push('/editor')" v-if="userStore.isLoggedIn">
              开始写作
            </a-button>
            <a-button size="large" class="btn-secondary" @click="$router.push('/login')" v-else>
              立即登录
            </a-button>
          </div>
        </div>
        <div class="hero-image">
          <div class="editor-preview">
            <div class="editor-header">
              <div class="editor-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div class="editor-title">小智笔记.md</div>
            </div>
            <div class="editor-body">
              <div class="editor-line">
                <span class="line-number">1</span>
                <span class="line-content"><span class="token-heading"># 欢迎使用小智笔记</span></span>
              </div>
              <div class="editor-line">
                <span class="line-number">2</span>
                <span class="line-content"></span>
              </div>
              <div class="editor-line">
                <span class="line-number">3</span>
                <span class="line-content">这是一个支持 <span class="token-bold">**Markdown**</span> 的笔记平台</span>
              </div>
              <div class="editor-line">
                <span class="line-number">4</span>
                <span class="line-content"></span>
              </div>
              <div class="editor-line">
                <span class="line-number">5</span>
                <span class="line-content"><span class="token-list">- 简洁优雅的编辑体验</span></span>
              </div>
              <div class="editor-line">
                <span class="line-number">6</span>
                <span class="line-content"><span class="token-list">- AI 智能写作辅助</span></span>
              </div>
              <div class="editor-line">
                <span class="line-number">7</span>
                <span class="line-content"><span class="token-list">- 多种主题自由切换</span></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="section-container">
        <div class="section-header">
          <h2>产品功能</h2>
          <p class="section-desc">全方位的写作解决方案，让创作更加高效</p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">
              <EditOutlined />
            </div>
            <h3>Markdown 编辑</h3>
            <p>支持标准 Markdown 语法，实时预览，让写作更加流畅</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <RobotOutlined />
            </div>
            <h3>AI 智能辅助</h3>
            <p>集成豆包 AI，提供续写、润色、扩写等智能写作功能</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <BgColorsOutlined />
            </div>
            <h3>主题切换</h3>
            <p>支持亮色/暗色模式，7 种主题色可选，个性化你的写作环境</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <CloudOutlined />
            </div>
            <h3>云端同步</h3>
            <p>笔记自动保存到云端，随时随地访问你的创作内容</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <span class="icon-text">🔗</span>
            </div>
            <h3>便捷分享</h3>
            <p>一键生成分享链接，让更多人看到你的精彩内容</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">
              <SafetyOutlined />
            </div>
            <h3>安全可靠</h3>
            <p>数据加密存储，保障你的创作内容安全无忧</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats">
      <div class="section-container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">{{ stats.article_count || 0 }}</div>
            <div class="stat-label">笔记总数</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.user_count || 0 }}</div>
            <div class="stat-label">注册用户</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.view_count || 0 }}</div>
            <div class="stat-label">总阅读量</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.comment_count || 0 }}</div>
            <div class="stat-label">评论数量</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Latest Articles -->
    <section class="articles">
      <div class="section-container">
        <div class="section-header">
          <h2>最新笔记</h2>
          <a-button type="link" @click="$router.push('/articles')">
            查看更多 <RightOutlined />
          </a-button>
        </div>
        <div class="articles-grid">
          <a-card
            v-for="article in articles"
            :key="article.id"
            class="article-card"
            hoverable
            @click="goToArticle(article.slug)"
          >
            <template #cover v-if="article.cover_image">
              <img :src="article.cover_image" :alt="article.title" />
            </template>
            <div class="article-category" v-if="article.category">
              {{ article.category.name }}
            </div>
            <h3 class="article-title">{{ article.title }}</h3>
            <p class="article-summary">{{ article.summary }}</p>
            <div class="article-meta">
              <span class="author">
                <UserOutlined /> {{ article.author?.nickname || article.author?.username }}
              </span>
              <span class="views">
                <EyeOutlined /> {{ article.view_count }}
              </span>
              <span class="likes">
                <LikeOutlined /> {{ article.like_count }}
              </span>
            </div>
          </a-card>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="section-container">
        <h2>开始你的创作之旅</h2>
        <p>加入小智笔记，记录你的想法，分享你的知识</p>
        <a-button type="primary" size="large" @click="$router.push(userStore.isLoggedIn ? '/editor' : '/register')">
          {{ userStore.isLoggedIn ? '开始写作' : '免费注册' }}
        </a-button>
      </div>
    </section>

    <!-- Open Source Section -->
    <section class="open-source">
      <div class="section-container">
        <div class="open-source-content">
          <h3>开源项目</h3>
          <p>小智笔记是一个开源项目，欢迎 Star 和贡献代码</p>
          <div class="repo-links">
            <a v-if="githubRepo" :href="githubRepo" target="_blank" rel="noopener noreferrer" class="repo-link github">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              <span>GitHub</span>
            </a>
            <a v-if="giteeRepo" :href="giteeRepo" target="_blank" rel="noopener noreferrer" class="repo-link gitee">
              <svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor">
                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.521 15.701c-.232 1.065-1.178 1.874-2.319 1.874H9.28c-1.299 0-2.357-1.058-2.357-2.357V9.28c0-1.299 1.058-2.357 2.357-2.357h5.922c1.299 0 2.357 1.058 2.357 2.357v1.178c0 .65-.529 1.178-1.178 1.178h-3.543c-.65 0-1.178.529-1.178 1.178v1.178c0 .65.529 1.178 1.178 1.178h2.364c.65 0 1.178.529 1.178 1.178v.357z"/>
              </svg>
              <span>Gitee</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  RightOutlined,
  UserOutlined,
  EyeOutlined,
  LikeOutlined,
  EditOutlined,
  RobotOutlined,
  BgColorsOutlined,
  CloudOutlined,
  SafetyOutlined
} from '@ant-design/icons-vue'
import { useUserStore } from '@/stores/user'
import { getArticles } from '@/api/article'
import { getStats } from '@/api/dashboard'

const githubRepo = computed(() => import.meta.env.VITE_GITHUB_URL || '')
const giteeRepo = computed(() => import.meta.env.VITE_GITEE_URL || '')

const router = useRouter()
const userStore = useUserStore()

const articles = ref([])
const stats = ref({})
const loading = ref(false)

const fetchArticles = async () => {
  loading.value = true
  try {
    const res = await getArticles({
      page: 1,
      size: 6,
      order_by: 'latest'
    })
    if (res.code === 200) {
      articles.value = res.data.items
    }
  } catch (error) {
    message.error('获取笔记失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await getStats()
    if (res.code === 200) {
      stats.value = res.data
    }
  } catch (error) {
    console.error('获取统计数据失败', error)
  }
}

const goToArticle = (slug) => {
  router.push(`/article/${slug}`)
}

onMounted(() => {
  fetchArticles()
  fetchStats()
})
</script>

<style scoped lang="less">
// Hero Section
.hero {
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  padding: 80px 24px;
  min-height: 600px;
  display: flex;
  align-items: center;

  .hero-container {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
    width: 100%;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
      text-align: center;
    }
  }

  .hero-content {
    .hero-title {
      font-size: 56px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 16px;
      line-height: 1.2;

      @media (max-width: 768px) {
        font-size: 40px;
      }
    }

    .hero-subtitle {
      font-size: 28px;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 16px;

      @media (max-width: 768px) {
        font-size: 22px;
      }
    }

    .hero-desc {
      font-size: 16px;
      color: var(--text-secondary);
      margin-bottom: 32px;
      line-height: 1.6;
    }

    .hero-actions {
      display: flex;
      gap: 16px;

      @media (max-width: 768px) {
        justify-content: center;
      }

      .btn-primary {
        background: #1890ff !important;
        border-color: #1890ff !important;
        color: #fff !important;
        padding: 0 32px;
        height: 48px;
        font-size: 16px;
        border-radius: 8px;

        &:hover {
          background: #40a9ff !important;
          border-color: #40a9ff !important;
        }
      }

      .btn-secondary {
        padding: 0 32px;
        height: 48px;
        font-size: 16px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        background: var(--bg-primary);
        color: var(--text-primary);

        &:hover {
          border-color: var(--ant-primary-color);
          color: var(--ant-primary-color);
        }
      }
    }
  }

  .hero-image {
    display: flex;
    justify-content: center;

    .editor-preview {
      width: 100%;
      max-width: 500px;
      background: var(--card-bg);
      border-radius: 12px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      overflow: hidden;
      border: 1px solid var(--border-color);

      .editor-header {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-color);

        .editor-dots {
          display: flex;
          gap: 8px;
          margin-right: 16px;

          span {
            width: 12px;
            height: 12px;
            border-radius: 50%;

            &:nth-child(1) { background: #ff5f56; }
            &:nth-child(2) { background: #ffbd2e; }
            &:nth-child(3) { background: #27c93f; }
          }
        }

        .editor-title {
          flex: 1;
          text-align: center;
          color: var(--text-secondary);
          font-size: 13px;
        }
      }

      .editor-body {
        padding: 16px;
        font-family: 'Fira Code', 'Consolas', monospace;
        font-size: 14px;
        line-height: 1.8;

        .editor-line {
          display: flex;

          .line-number {
            width: 30px;
            color: var(--text-tertiary);
            text-align: right;
            margin-right: 16px;
            user-select: none;
          }

          .line-content {
            flex: 1;
            color: var(--text-primary);

            .token-heading {
              color: var(--ant-primary-color);
              font-weight: 600;
            }

            .token-bold {
              font-weight: 600;
              color: var(--text-primary);
            }

            .token-list {
              color: var(--text-secondary);
            }
          }
        }
      }
    }
  }
}

// Section Common Styles
.section-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;

  h2 {
    font-size: 36px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
  }

  .section-desc {
    font-size: 16px;
    color: var(--text-secondary);
  }
}

// Features Section
.features {
  padding: 80px 0;
  background: var(--bg-primary);

  .features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;

    @media (max-width: 992px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 576px) {
      grid-template-columns: 1fr;
    }
  }

  .feature-card {
    padding: 32px;
    background: var(--card-bg);
    border-radius: 12px;
    border: 1px solid var(--border-color);
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
      border-color: var(--ant-primary-color);
    }

    .feature-icon {
      width: 56px;
      height: 56px;
      background: #1890ff;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 20px;

      :deep(.anticon) {
        font-size: 28px;
        color: #fff;
      }

      .icon-text {
        font-size: 28px;
        line-height: 1;
      }
    }

    h3 {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
    }

    p {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.6;
    }
  }
}

// Stats Section
.stats {
  padding: 60px 0;
  background: #1890ff;

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24px;
    text-align: center;

    @media (max-width: 768px) {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  .stat-item {
    .stat-number {
      font-size: 48px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 8px;

      @media (max-width: 768px) {
        font-size: 36px;
      }
    }

    .stat-label {
      font-size: 16px;
      color: rgba(255, 255, 255, 0.8);
    }
  }
}

// Articles Section
.articles {
  padding: 80px 0;
  background: var(--bg-secondary);

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin-bottom: 0;
    }
  }

  .articles-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;

    @media (max-width: 992px) {
      grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 576px) {
      grid-template-columns: 1fr;
    }
  }

  .article-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
    }

    :deep(.ant-card-cover) {
      height: 180px;
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
      }
    }

    &:hover :deep(.ant-card-cover img) {
      transform: scale(1.05);
    }

    :deep(.ant-card-body) {
      padding: 20px;
    }

    .article-category {
      display: inline-block;
      padding: 4px 12px;
      background: var(--ant-primary-color);
      color: #fff;
      font-size: 12px;
      border-radius: 4px;
      margin-bottom: 12px;
    }

    .article-title {
      font-size: 18px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .article-summary {
      font-size: 14px;
      color: var(--text-secondary);
      line-height: 1.6;
      margin-bottom: 16px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }

    .article-meta {
      display: flex;
      gap: 16px;
      font-size: 13px;
      color: var(--text-tertiary);

      span {
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }
  }
}

// CTA Section
.cta {
  padding: 80px 24px;
  background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
  text-align: center;

  h2 {
    font-size: 36px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 16px;
  }

  p {
    font-size: 16px;
    color: var(--text-secondary);
    margin-bottom: 32px;
  }

  .ant-btn {
    background: #1890ff !important;
    border-color: #1890ff !important;
    color: #fff !important;
    padding: 0 48px;
    height: 52px;
    font-size: 16px;
    border-radius: 8px;

    &:hover {
      background: #40a9ff !important;
      border-color: #40a9ff !important;
    }
  }
}

// Open Source Section
.open-source {
  padding: 60px 24px;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);

  .open-source-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;

    h3 {
      font-size: 28px;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 12px;
    }

    p {
      font-size: 16px;
      color: var(--text-secondary);
      margin-bottom: 32px;
    }

    .repo-links {
      display: flex;
      justify-content: center;
      gap: 24px;
      flex-wrap: wrap;

      .repo-link {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 14px 28px;
        border-radius: 8px;
        text-decoration: none;
        font-size: 16px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

        svg {
          width: 24px;
          height: 24px;
        }

        &.github {
          background: #24292e;
          color: #fff;

          &:hover {
            background: #444d56;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(36, 41, 46, 0.3);
          }
        }

        &.gitee {
          background: #c71d23;
          color: #fff;

          &:hover {
            background: #e63037;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(199, 29, 35, 0.3);
          }
        }
      }
    }
  }

  @media (max-width: 768px) {
    padding: 40px 24px;

    .open-source-content {
      h3 {
        font-size: 24px;
      }

      .repo-links {
        flex-direction: column;
        align-items: center;

        .repo-link {
          width: 100%;
          max-width: 280px;
          justify-content: center;
        }
      }
    }
  }
}
</style>
