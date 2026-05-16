<template>
  <div class="page-container article-detail-page">
    <a-skeleton v-if="loading" active :paragraph="{ rows: 10 }" />

    <template v-else-if="article">
      <!-- 左侧边栏：作者信息 + 目录 -->
      <div class="article-sidebar">
        <!-- 作者信息卡片 -->
        <div class="author-card" v-if="article.author">
          <div class="author-card-header">
            <a-avatar :src="article.author.avatar" :size="48" />
            <div class="author-card-info">
              <div class="author-card-name">{{ article.author.nickname || article.author.username }}</div>
              <div class="author-card-bio">{{ article.author.bio || '暂无简介' }}</div>
            </div>
          </div>
          <a-divider style="margin: 12px 0" />
          <div class="author-card-stats">
            <div class="author-stat-item">
              <div class="author-stat-value">{{ article.author.article_count || 0 }}</div>
              <div class="author-stat-label">笔记</div>
            </div>
            <div class="author-stat-item">
              <div class="author-stat-value">{{ article.author.total_likes || 0 }}</div>
              <div class="author-stat-label">获赞</div>
            </div>
            <div class="author-stat-item">
              <div class="author-stat-value">{{ getJoinDays(article.author.created_at) }}</div>
              <div class="author-stat-label">入站天数</div>
            </div>
          </div>
        </div>

        <!-- 目录导航 -->
        <div class="article-toc" v-if="toc.length > 0">
          <div class="toc-title">目录</div>
          <div ref="tocListRef" class="toc-list">
            <div
              v-for="(item, index) in toc"
              :key="item.id"
              :ref="el => { if (el) tocItemRefs[index] = el }"
              class="toc-item"
              :class="{ active: activeTocId === item.id, [`toc-level-${item.level}`]: true }"
              @click="scrollToHeading(item.id)"
            >
              {{ item.text }}
            </div>
          </div>
        </div>
      </div>

      <div class="article-main">
        <div class="article-cover-image" v-if="article.cover_image">
          <img :src="getImageUrl(article.cover_image)" :alt="article.title" />
        </div>
        <div class="article-header">
          <h1 class="article-title">{{ article.title }}</h1>
          <div class="article-meta">
            <a-avatar :src="article.author?.avatar" />
            <span>{{ article.author?.nickname || article.author?.username }}</span>
            <a-divider type="vertical" />
            <span>{{ formatDate(article.published_at) }}</span>
            <a-divider type="vertical" />
            <span
              v-if="article.category"
              class="category-text"
              @click="router.push('/categories?active=' + article.category.id)"
            >
              <FolderOutlined /> {{ article.category.name }}
            </span>
            <a-divider type="vertical" v-if="article.category" />
            <span><EyeOutlined /> {{ article.view_count }}</span>
            <span><LikeOutlined /> {{ article.like_count }}</span>
            <span><MessageOutlined /> {{ article.comment_count }}</span>
          </div>
        </div>

        <div ref="contentRef" class="article-content markdown-content" :class="themeStore.isDark ? 'dark-code' : 'light-code'" v-html="renderedContent"></div>

        <div class="article-tags article-tags-bottom" v-if="article.tags?.length">
          <a-tag
            v-for="tag in article.tags"
            :key="tag.id"
            :color="tag.color"
            class="article-tag-link"
            @click="goToTag(tag.id)"
          >
            #{{ tag.name }}
          </a-tag>
        </div>

        <a-divider />

        <div class="article-actions">
          <!-- 编辑按钮 - 仅管理员或作者可见 -->
          <a-button 
            v-if="userStore.isLoggedIn && (userStore.isAdmin || article.author?.id === userStore.userInfo?.id)"
            type="primary" 
            shape="circle" 
            size="large" 
            @click="handleEdit"
          >
            <EditOutlined />
          </a-button>
          <a-button
            :type="article.is_liked ? 'primary' : 'default'"
            shape="circle"
            size="large"
            @click="handleLike"
            :loading="likeLoading"
          >
            <LikeOutlined />
          </a-button>
          <a-button shape="circle" size="large" @click="handleShare">
            <ShareAltOutlined />
          </a-button>
        </div>

        <!-- 评论区域 -->
        <div class="comment-section">
          <h3 class="comment-title">评论 ({{ article.comment_count }})</h3>

          <!-- 发表评论 -->
          <div class="comment-input-wrapper" v-if="userStore.isLoggedIn">
            <a-textarea
              v-model:value="commentContent"
              placeholder="发表你的评论..."
              :rows="3"
            />
            <div class="comment-submit">
              <a-button type="primary" @click="submitComment" :loading="commentLoading">
                发表评论
              </a-button>
            </div>
          </div>
          <div v-else class="comment-login-tip">
            <a-button type="link" @click="router.push('/login')">登录后即可发表评论</a-button>
          </div>

          <!-- 评论列表 -->
          <div class="comment-list">
            <CommentItem
              v-for="comment in comments"
              :key="comment.id"
              :comment="comment"
              :current-user-id="userStore.userInfo?.id"
              :article-author-id="article?.author?.id"
              :is-admin="userStore.isAdmin"
              :active-reply-id="activeReplyId"
              :is-submitting="commentLoading"
              is-root
              @reply="handleReplyClick"
              @cancel-reply="handleCancelReply"
              @submit-reply="handleSubmitReply"
              @delete="handleDeleteComment"
            />
          </div>
        </div>
      </div>
    </template>

    <a-empty v-else description="笔记不存在" class="not-found-empty" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { EyeOutlined, LikeOutlined, MessageOutlined, ShareAltOutlined, EditOutlined } from '@ant-design/icons-vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'
import { getArticle } from '@/api/article'
import { toggleLike } from '@/api/like'
import { getArticleComments, createComment, deleteComment } from '@/api/comment'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import { useSiteConfigStore } from '@/stores/siteConfig'
import CommentItem from '@/components/CommentItem.vue'
import { formatDate } from '@/utils/date'
import { getImageUrl } from '@/utils/image'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const userStore = useUserStore()
const siteConfigStore = useSiteConfigStore()

const article = ref(null)
const loading = ref(false)
const likeLoading = ref(false)
const comments = ref([])
const commentContent = ref('')
const commentLoading = ref(false)
const activeReplyId = ref(null)
const contentRef = ref(null)
const toc = ref([])
const activeTocId = ref('')
const tocListRef = ref(null)
const tocItemRefs = ref([])

// 笔记加载完成后重新生成目录（确保 DOM 已渲染）
watch(loading, (newLoading) => {
  if (!newLoading && article.value) {
    generateToc()
  }
})

// MarkdownIt 配置：为标题添加锚点ID
const md = new MarkdownIt({
  highlight: (code, lang) => {
    let highlighted
    if (lang && hljs.getLanguage(lang)) {
      highlighted = hljs.highlight(code, { language: lang }).value
    } else {
      highlighted = hljs.highlightAuto(code).value
      lang = 'text'
    }
    return `<pre class="hljs"><div class="code-header"><span class="code-lang">${lang}</span><button class="code-copy-btn" data-code="${encodeURIComponent(code)}"><span class="copy-icon"><svg viewBox="64 64 896 896" fill="currentColor" width="1em" height="1em"><path d="M832 64H296c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h496v688c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V96c0-17.7-14.3-32-32-32zM704 192H192c-17.7 0-32 14.3-32 32v530.7c0 8.5 3.4 16.6 9.4 22.6l173.3 173.3c2.8 2.8 6.3 5.1 10.1 6.5V752c0 17.7 14.3 32 32 32h352c17.7 0 32-14.3 32-32V224c0-17.7-14.3-32-32-32zM344 712a40 40 0 1080 0 40 40 0 10-80 0z"/></svg></span><span class="copy-text">复制</span></button></div><code>${highlighted}</code></pre>`
  }
})

// 自定义渲染规则：为 h2/h3 添加 id
const slugify = (text) => {
  return text.toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, '-').replace(/^-|-$/g, '')
}

md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
  const token = tokens[idx]
  if (token.tag === 'h1' || token.tag === 'h2' || token.tag === 'h3') {
    const inlineToken = tokens[idx + 1]
    const text = inlineToken ? inlineToken.content : ''
    const id = `heading-${slugify(text)}-${idx}`
    token.attrSet('id', id)
    token.attrSet('data-toc-id', id)
  }
  return self.renderToken(tokens, idx, options)
}

const renderedContent = computed(() => {
  if (!article.value?.content) return ''
  return md.render(article.value.content)
})

// 监听笔记内容变化，重新生成目录
watch(renderedContent, () => {
  generateToc()
})

// 生成目录
const generateToc = () => {
  nextTick(() => {
    if (!contentRef.value) return
    let headings = contentRef.value.querySelectorAll('h1[data-toc-id], h2[data-toc-id], h3[data-toc-id]')

    // Fallback: if no headings with data-toc-id, try plain h1/h2/h3
    // (handles HTML content or edge cases where custom renderer didn't apply)
    if (headings.length === 0) {
      const plainHeadings = contentRef.value.querySelectorAll('h1, h2, h3')
      plainHeadings.forEach((heading, index) => {
        if (!heading.getAttribute('data-toc-id')) {
          const text = heading.textContent || ''
          const id = `heading-fallback-${slugify(text)}-${index}`
          heading.id = id
          heading.setAttribute('data-toc-id', id)
        }
      })
      headings = contentRef.value.querySelectorAll('h1[data-toc-id], h2[data-toc-id], h3[data-toc-id]')
    }

    const items = []
    headings.forEach((heading) => {
      items.push({
        id: heading.getAttribute('data-toc-id'),
        text: heading.textContent,
        level: heading.tagName === 'H1' ? 1 : (heading.tagName === 'H2' ? 2 : 3)
      })
    })
    toc.value = items
  })
}

// 滚动到指定标题
const scrollToHeading = (id) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// 滚动监听高亮目录
const handleScroll = () => {
  if (!contentRef.value || toc.value.length === 0) return
  const headings = contentRef.value.querySelectorAll('h1[data-toc-id], h2[data-toc-id], h3[data-toc-id]')
  const scrollTop = window.scrollY + 100
  let current = ''
  headings.forEach((heading) => {
    if (heading.offsetTop <= scrollTop) {
      current = heading.getAttribute('data-toc-id')
    }
  })
  if (current && current !== activeTocId.value) {
    activeTocId.value = current
    // 自动滚动目录到当前活跃的章节
    scrollToActiveToc()
  }
}

// 滚动目录列表，使当前活跃的目录项可见
const scrollToActiveToc = () => {
  nextTick(() => {
    if (!tocListRef.value || !tocItemRefs.value.length) return
    
    const activeIndex = toc.value.findIndex(item => item.id === activeTocId.value)
    if (activeIndex === -1) return
    
    const activeElement = tocItemRefs.value[activeIndex]
    if (!activeElement) return
    
    const container = tocListRef.value
    const containerRect = container.getBoundingClientRect()
    const elementRect = activeElement.getBoundingClientRect()
    
    // 计算需要滚动的距离
    const offset = elementRect.top - containerRect.top - containerRect.height / 3
    container.scrollTop += offset
  })
}

const goToTag = (tagId) => {
  router.push({ path: '/articles', query: { tag: tagId } })
}

const getJoinDays = (createdAt) => {
  if (!createdAt) return 0
  const utcStr = createdAt.includes('+') || createdAt.endsWith('Z') ? createdAt : createdAt + 'Z'
  const joinDate = dayjs(utcStr)
  const now = dayjs()
  return now.diff(joinDate, 'day')
}

const fetchArticle = async () => {
  loading.value = true
  try {
    const res = await getArticle(route.params.slug)
    if (res.code === 200) {
      article.value = res.data
      await fetchComments(res.data.id)
      generateToc()
    }
  } catch (error) {
    message.error('获取笔记失败')
  } finally {
    loading.value = false
  }
}

const fetchComments = async (articleId) => {
  try {
    const res = await getArticleComments(articleId)
    if (res.code === 200) {
      comments.value = res.data.items || []
      // 如果有 comment_id 参数，滚动到对应评论
      const commentId = route.query.comment_id
      if (commentId) {
        nextTick(() => {
          const el = document.getElementById(`comment-${commentId}`)
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' })
            el.classList.add('comment-highlight')
            setTimeout(() => el.classList.remove('comment-highlight'), 3000)
          }
        })
      }
    }
  } catch (error) {
    console.error('获取评论失败', error)
  }
}

const handleLike = async () => {
  if (!userStore.isLoggedIn) {
    message.info('请先登录')
    router.push('/login')
    return
  }
  likeLoading.value = true
  try {
    const res = await toggleLike(article.value.id)
    if (res.code === 200) {
      article.value.is_liked = res.data.is_liked
      article.value.like_count = res.data.like_count
      message.success(res.message)
    }
  } catch (error) {
    message.error('操作失败')
  } finally {
    likeLoading.value = false
  }
}

const handleShare = () => {
  const url = window.location.href
  navigator.clipboard.writeText(url).then(() => {
    message.success('链接已复制到剪贴板')
  }).catch(() => {
    message.error('复制失败')
  })
}

const handleEdit = () => {
  // 跳转到编辑器页面
  router.push(`/editor/${article.value.id}`)
}

const handleReplyClick = (comment) => {
  if (!userStore.isLoggedIn) {
    message.info('请先登录')
    router.push('/login')
    return
  }
  activeReplyId.value = comment.id
}

const handleCancelReply = () => {
  activeReplyId.value = null
}

const handleSubmitReply = async ({ parent_id, content }) => {
  commentLoading.value = true
  try {
    const res = await createComment(article.value.id, { content, parent_id })
    if (res.code === 200) {
      message.success('回复成功')
      activeReplyId.value = null
      await fetchComments(article.value.id)
      article.value.comment_count += 1
    }
  } catch (error) {
    message.error('回复失败')
  } finally {
    commentLoading.value = false
  }
}

const submitComment = async () => {
  if (!commentContent.value.trim()) {
    message.warning('请输入评论内容')
    return
  }
  commentLoading.value = true
  try {
    const res = await createComment(article.value.id, {
      content: commentContent.value.trim(),
      parent_id: null
    })
    if (res.code === 200) {
      message.success('评论成功')
      commentContent.value = ''
      await fetchComments(article.value.id)
      article.value.comment_count += 1
    }
  } catch (error) {
    message.error('发表评论失败')
  } finally {
    commentLoading.value = false
  }
}

const handleDeleteComment = async (comment) => {
  try {
    const res = await deleteComment(comment.id)
    if (res.code === 200) {
      message.success('删除成功')
      await fetchComments(article.value.id)
      article.value.comment_count = Math.max(0, article.value.comment_count - 1)
    }
  } catch (error) {
    message.error('删除失败')
  }
}

// 复制代码
const handleCopyClick = (e) => {
  const btn = e.target.closest('.code-copy-btn')
  if (!btn) return

  const code = decodeURIComponent(btn.dataset.code)
  const customSuffix = siteConfigStore.codeCopySuffix || ''
  const articleUrl = window.location.href
  const attribution = `------源自小智笔记，尊重作者版权，注明出处\n${articleUrl}`
  const textToCopy = customSuffix
    ? code + '\n\n' + customSuffix + '\n\n' + attribution
    : code + '\n\n' + attribution
  navigator.clipboard.writeText(textToCopy).then(() => {
    const originalText = btn.innerHTML
    btn.innerHTML = '<span class="copy-icon"><svg viewBox="64 64 896 896" fill="currentColor" width="1em" height="1em"><path d="M912 190h-69.9c-9.8 0-19.1 4.5-25.1 12.2L404.7 724.5 207 474a32 32 0 00-25.1-12.2H112c-6.7 0-10.4 7.7-6.3 12.9l273.9 347c12.8 16.2 37.4 16.2 50.3 0l488.4-618.9c4.1-5.1.4-12.8-6.3-12.8z"/></svg></span><span class="copy-text">已复制</span>'
    btn.classList.add('copied')
    message.success('代码已复制')
    setTimeout(() => {
      btn.innerHTML = originalText
      btn.classList.remove('copied')
    }, 2000)
  }).catch(() => {
    message.error('复制失败')
  })
}

onMounted(() => {
  fetchArticle()
  document.addEventListener('click', handleCopyClick)
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  document.removeEventListener('click', handleCopyClick)
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped lang="less">
// Remove grid from here - now applied to parent .content in MainLayout
.article-detail-page {
  // Reset to allow parent background to show through
  background: transparent;
}

.article-cover-image {
  width: 100%;
  max-width: 900px;
  margin: 0 auto 24px;
  border-radius: 12px;
  overflow: hidden;

  img {
    width: 100%;
    height: auto;
    max-height: 400px;
    object-fit: cover;
    display: block;
  }
}

.article-header {
  margin-bottom: 32px;
  text-align: center;

  .article-title {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 16px;
  }
  
  .article-meta {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: var(--text-secondary);
    margin-bottom: 16px;
    flex-wrap: wrap;

    .category-text {
      cursor: pointer;
      transition: color 0.2s;

      &:hover {
        color: var(--ant-primary-color);
      }
    }
  }
  
  .article-tags {
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;

    .article-tag-link {
      cursor: pointer;
      transition: transform 0.2s ease, opacity 0.2s ease;

      &:hover {
        transform: translateY(-2px);
        opacity: 0.85;
      }
    }
  }

  .article-tags-bottom {
    justify-content: flex-start;
    margin: 16px 0 8px;
  }
}

.article-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 0;

  // 代码块
  :deep(.hljs) {
    margin: 16px 0;
    border-radius: 8px;
    overflow: hidden;
    background: #1e1e1e;

    .code-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 16px;
      background: #2d2d2d;
      border-bottom: 1px solid #3d3d3d;

      .code-lang {
        font-size: 12px;
        color: #9cdcfe;
        text-transform: uppercase;
      }

      .code-copy-btn {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 4px;
        background: transparent;
        color: #858585;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        border: none;

        .copy-icon {
          display: inline-flex;
          align-items: center;
          width: 14px;
          height: 14px;
        }

        &:hover {
          color: #fff;
        }

        &.copied {
          color: #98c379;
        }
      }
    }

    code {
      display: block;
      padding: 16px;
      overflow-x: auto;
      background: transparent;
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 13.5px;
      line-height: 1.7;
    }
  }

  // 白天模式代码块 — 与黑夜模式统一风格
  &.light-code :deep(.hljs) {
    background: #1e1e1e;

    .code-header {
      background: #2d2d2d;
      border-bottom-color: #3d3d3d;
    }
  }

  :deep(h1) {
    font-size: 28px;
    font-weight: 700;
    margin: 24px 0 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--border-color);
  }

  :deep(h2) {
    font-size: 22px;
    font-weight: 600;
    margin: 20px 0 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-color);
  }

  :deep(h3) {
    font-size: 18px;
    font-weight: 600;
    margin: 16px 0 10px;
  }

  :deep(p) {
    margin: 12px 0;
    line-height: 1.8;
  }

  :deep(ul), :deep(ol) {
    margin: 12px 0;
    padding-left: 24px;
  }

  :deep(li) {
    margin: 6px 0;
  }

  :deep(blockquote) {
    margin: 16px 0;
    padding: 12px 16px;
    border-left: 4px solid var(--ant-primary-color);
    background: var(--bg-secondary);
    border-radius: 0 8px 8px 0;

    p {
      margin: 0;
    }
  }

  :deep(code) {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 14px;
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  }

  :deep(a) {
    color: var(--ant-primary-color);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }

  :deep(img) {
    max-width: 100%;
    border-radius: 8px;
    margin: 12px 0;
  }

  :deep(hr) {
    border: none;
    border-top: 2px solid var(--border-color);
    margin: 24px 0;
  }

  :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;

    th, td {
      padding: 10px 16px;
      border: 1px solid var(--border-color);
      text-align: left;
    }

    th {
      background: var(--bg-secondary);
      font-weight: 600;
    }
  }
}

.article-detail-page {
  display: flex;
  gap: 32px;
  position: relative;

  .article-main {
    flex: 1;
    min-width: 0;
  }

  .article-sidebar {
    width: 220px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 16px;
    position: sticky;
    top: 80px;
    align-self: flex-start;
    max-height: calc(100vh - 120px);
    overflow-y: auto;

    .author-card {
      padding: 16px;
      background: var(--card-bg, #fff);
      border: 1px solid var(--border-color, #f0f0f0);
      border-radius: 8px;
      flex-shrink: 0;

      .author-card-header {
        display: flex;
        align-items: center;
        gap: 12px;

        .author-card-info {
          flex: 1;
          min-width: 0;

          .author-card-name {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          .author-card-bio {
            font-size: 12px;
            color: var(--text-tertiary);
            margin-top: 4px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
      }

      .author-card-stats {
        display: flex;
        justify-content: space-around;
        text-align: center;

        .author-stat-item {
          .author-stat-value {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-primary);
          }

          .author-stat-label {
            font-size: 12px;
            color: var(--text-tertiary);
            margin-top: 2px;
          }
        }
      }
    }

    .article-toc {
      padding: 16px;
      background: var(--card-bg, #fff);
      border: 1px solid var(--border-color, #f0f0f0);
      border-radius: 8px;
      flex-shrink: 0;

      .toc-title {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        color: var(--text-primary);
      }

      .toc-list {
        max-height: 50vh;
        overflow-y: auto;
        overflow-x: hidden;
        scrollbar-width: thin;
        scrollbar-color: var(--border-color, #f0f0f0) transparent;
        
        &::-webkit-scrollbar {
          width: 4px;
        }
        
        &::-webkit-scrollbar-track {
          background: transparent;
        }
        
        &::-webkit-scrollbar-thumb {
          background-color: var(--border-color, #f0f0f0);
          border-radius: 2px;
        }
        
        .toc-item {
          padding: 6px 8px;
          cursor: pointer;
          border-radius: 4px;
          font-size: 14px;
          color: var(--text-secondary);
          transition: all 0.2s ease;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;

          &:hover {
            background: var(--bg-secondary);
            color: var(--ant-primary-color);
          }

          &.active {
            background: var(--ant-primary-1, #e6f7ff);
            color: var(--ant-primary-color);
            font-weight: 500;
          }
        }

        .toc-level-1 {
          font-weight: 600;
          font-size: 15px;
        }

        .toc-level-3 {
          padding-left: 20px;
          font-size: 13px;
        }
      }
    }
  }

  @media (max-width: 1024px) {
    .article-sidebar {
      display: none;
    }
  }
}

.article-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  align-items: center;
  padding: 24px 0;
}

.comment-section {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 0;

  .comment-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 24px;
    color: var(--text-primary);
  }

  .comment-input-wrapper {
    margin-bottom: 32px;

    .comment-submit {
      display: flex;
      justify-content: flex-end;
      gap: 12px;
      margin-top: 12px;
    }
  }

  .comment-login-tip {
    text-align: center;
    padding: 24px;
    margin-bottom: 32px;
    background: var(--bg-secondary);
    border-radius: 8px;
  }

  .comment-list {
    padding-top: 8px;
  }
}

.comment-highlight {
  animation: highlight-pulse 3s ease;
}

@keyframes highlight-pulse {
  0% {
    background: rgba(24, 144, 255, 0.15);
    border-radius: 8px;
  }
  100% {
    background: transparent;
  }
}

.not-found-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
  width: 100%;
}

:deep(.not-found-empty .ant-empty-description) {
  color: var(--text-secondary);
}
:deep(.not-found-empty .ant-empty-description) {
  color: var(--text-secondary);
}
</style>
