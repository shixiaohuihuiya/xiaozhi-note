<template>
  <div class="page-container about-page">
    <!-- Hero Section -->
    <section class="about-hero">
      <h1>关于小智笔记</h1>
      <p class="subtitle">智能写作助手，让创作更轻松</p>
      <p class="desc">
        小智笔记是一款现代化的写作平台，集成 AI 智能辅助功能，
        帮助用户更高效地进行内容创作。无论是技术博客、生活随笔还是专业文档，
        小智笔记都能为您提供优质的写作体验。
      </p>
    </section>

    <!-- Author Section -->
    <section class="author-section">
      <div class="author-card">
        <div class="author-avatar">
          <span>🧑‍💻</span>
        </div>
        <div class="author-info">
          <h2>关于博主</h2>
          <p class="author-name">是小灰灰呀</p>
          <p class="author-desc">
            热爱技术与写作的开发者，致力于构建简洁高效的写作工具。
            相信好的工具能够激发创作灵感，让每个人都能享受写作的乐趣。
          </p>
          <div class="author-links">
            <a-button v-if="githubRepo" type="primary" shape="round" :href="githubRepo" target="_blank">
              <GithubOutlined /> GitHub
            </a-button>
            <a-button v-if="giteeRepo" shape="round" :href="giteeRepo" target="_blank">
              <GitlabOutlined /> Gitee
            </a-button>
          </div>
          <div class="author-stats">
            <div class="stat">
              <span class="stat-value">100+</span>
              <span class="stat-label">原创笔记</span>
            </div>
            <div class="stat">
              <span class="stat-value">50+</span>
              <span class="stat-label">技术分享</span>
            </div>
            <div class="stat">
              <span class="stat-value">1w+</span>
              <span class="stat-label">阅读量</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <h2>核心功能</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">✍️</div>
          <h3>Markdown 编辑</h3>
          <p>支持标准 Markdown 语法，实时预览，所见即所得</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🤖</div>
          <h3>AI 智能辅助</h3>
          <p>集成豆包 AI，提供续写、润色、扩写等智能写作功能</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">🎨</div>
          <h3>多主题切换</h3>
          <p>支持亮色/暗色模式，7 种主题色可选</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">☁️</div>
          <h3>云端同步</h3>
          <p>笔记自动保存到云端，随时随地访问您的创作</p>
        </div>
      </div>
    </section>

    <!-- Tech Stack Section -->
    <section class="tech-section">
      <h2>技术栈</h2>
      <div class="tech-grid">
        <div class="tech-card">
          <h3>前端</h3>
          <ul>
            <li>Vue 3 + Vite</li>
            <li>Ant Design Vue</li>
            <li>Pinia 状态管理</li>
            <li>Vue Router</li>
          </ul>
        </div>
        <div class="tech-card">
          <h3>后端</h3>
          <ul>
            <li>FastAPI (Python)</li>
            <li>SQLAlchemy 2.0</li>
            <li>MySQL 数据库</li>
            <li>JWT 认证</li>
          </ul>
        </div>
        <div class="tech-card">
          <h3>AI 能力</h3>
          <ul>
            <li>豆包大模型</li>
            <li>智能续写</li>
            <li>笔记润色</li>
            <li>内容扩写</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- Contact Section -->
    <section class="contact-section">
      <h2>联系我们</h2>
      <p>如果您有任何问题或建议，欢迎通过以下方式联系我们</p>
      <div class="contact-links">
        <a-button type="primary" size="large" @click="$router.push('/guestbook')">
          留言墙
        </a-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { GithubOutlined, GitlabOutlined } from '@ant-design/icons-vue'

// 从仓库链接提取个人主页链接
const githubRepo = computed(() => {
  const url = import.meta.env.VITE_GITHUB_URL || ''
  if (!url) return ''
  // 提取 https://github.com/username 部分
  const match = url.match(/^(https?:\/\/github\.com\/[\w-]+)/)
  return match ? match[1] : ''
})

const giteeRepo = computed(() => {
  const url = import.meta.env.VITE_GITEE_URL || ''
  if (!url) return ''
  // 提取 https://gitee.com/username 部分
  const match = url.match(/^(https?:\/\/gitee\.com\/[\w-]+)/)
  return match ? match[1] : ''
})
</script>

<style scoped lang="less">
.about-page {
  padding: 48px 24px;
}

.author-section {
  margin-bottom: 64px;

  .author-card {
    display: flex;
    gap: 32px;
    align-items: center;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;

    @media (max-width: 576px) {
      flex-direction: column;
      text-align: center;
    }
  }

  .author-avatar {
    width: 120px;
    height: 120px;
    background: var(--bg-secondary);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 64px;
    flex-shrink: 0;
  }

  .author-info {
    flex: 1;

    h2 {
      font-size: 14px;
      color: var(--text-tertiary);
      margin-bottom: 8px;
      font-weight: normal;
    }

    .author-name {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 12px;
    }

    .author-desc {
      color: var(--text-secondary);
      line-height: 1.8;
      margin-bottom: 24px;
    }
  }

  .author-links {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;

    @media (max-width: 576px) {
      justify-content: center;
    }
  }

  .author-stats {
    display: flex;
    gap: 32px;

    @media (max-width: 576px) {
      justify-content: center;
    }

    .stat {
      text-align: center;

      .stat-value {
        display: block;
        font-size: 24px;
        font-weight: 700;
        color: var(--ant-primary-color);
      }

      .stat-label {
        font-size: 13px;
        color: var(--text-tertiary);
      }
    }
  }
}

.about-hero {
  text-align: center;
  margin-bottom: 64px;
  
  h1 {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 16px;
  }
  
  .subtitle {
    font-size: 24px;
    color: var(--ant-primary-color);
    margin-bottom: 24px;
  }
  
  .desc {
    font-size: 16px;
    color: var(--text-secondary);
    line-height: 1.8;
    max-width: 700px;
    margin: 0 auto;
  }
}

.features-section {
  margin-bottom: 64px;
  
  h2 {
    text-align: center;
    font-size: 32px;
    margin-bottom: 32px;
  }
  
  .features-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
    max-width: 800px;
    margin: 0 auto;
    
    @media (max-width: 576px) {
      grid-template-columns: 1fr;
    }
  }
  
  .feature-card {
    text-align: center;
    padding: 32px;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    
    .feature-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
    
    h3 {
      font-size: 20px;
      margin-bottom: 12px;
    }
    
    p {
      color: var(--text-secondary);
      line-height: 1.6;
    }
  }
}

.tech-section {
  margin-bottom: 64px;
  
  h2 {
    text-align: center;
    font-size: 32px;
    margin-bottom: 32px;
  }
  
  .tech-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    max-width: 900px;
    margin: 0 auto;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .tech-card {
    padding: 24px;
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    
    h3 {
      font-size: 20px;
      margin-bottom: 16px;
      color: var(--ant-primary-color);
    }
    
    ul {
      list-style: none;
      padding: 0;
      margin: 0;
      
      li {
        padding: 8px 0;
        color: var(--text-secondary);
        border-bottom: 1px solid var(--border-color);
        
        &:last-child {
          border-bottom: none;
        }
      }
    }
  }
}

.contact-section {
  text-align: center;
  
  h2 {
    font-size: 32px;
    margin-bottom: 16px;
  }
  
  p {
    color: var(--text-secondary);
    margin-bottom: 24px;
  }
  
  .contact-links {
    display: flex;
    justify-content: center;
    gap: 16px;
  }
}
</style>
