<template>
  <div class="editor-page">
    <!-- 顶部工具栏 -->
    <div class="editor-toolbar">
      <a-input
        v-model:value="article.title"
        placeholder="请输入笔记标题..."
        class="title-input"
        size="large"
      />
      <div class="toolbar-meta">
        <!-- 封面图片 -->
        <div class="cover-uploader">
          <a-input
            v-model:value="article.cover_image"
            placeholder="封面图片链接或上传..."
            style="width: 200px"
            allow-clear
          >
            <template #prefix>
              <PictureOutlined />
            </template>
          </a-input>
          <a-upload
            :show-upload-list="false"
            :before-upload="beforeCoverUpload"
            :custom-request="handleCoverUpload"
            accept="image/*"
          >
            <a-button size="small" :loading="coverUploading">
              <UploadOutlined />
            </a-button>
          </a-upload>
        </div>
        <a-select
          v-model:value="article.category_id"
          placeholder="选择分类"
          style="width: 150px"
          :options="categories.map(c => ({ label: c.name, value: c.id }))"
          allow-clear
          show-search
        />
        <a-select
          v-model:value="article.tag_ids"
          mode="multiple"
          placeholder="选择标签"
          style="width: 200px"
          :options="tags.map(t => ({ label: '#' + t.name, value: t.id }))"
          allow-clear
          show-search
        />
      </div>
      <div class="toolbar-actions">
        <a-button @click="showAiAssistant = !showAiAssistant">
          <RobotOutlined /> AI助手
        </a-button>
        <a-button type="primary" @click="saveArticle" :loading="saving">
          {{ article.needs_reapproval ? '申请发布' : '发布笔记' }}
        </a-button>
      </div>
    </div>

    <!-- Markdown 格式工具栏 -->
    <div class="markdown-toolbar">
      <a-tooltip title="粗体">
        <a-button type="text" size="small" @click="insertFormat('**', '**', '粗体文字')">
          <BoldOutlined />
        </a-button>
      </a-tooltip>
      <a-tooltip title="斜体">
        <a-button type="text" size="small" @click="insertFormat('*', '*', '斜体文字')">
          <ItalicOutlined />
        </a-button>
      </a-tooltip>
      <a-divider type="vertical" />
      <a-tooltip title="标题">
        <a-button type="text" size="small" @click="insertFormat('## ', '', '标题')">
          <FontSizeOutlined />
        </a-button>
      </a-tooltip>
      <a-tooltip title="引用">
        <a-button type="text" size="small" @click="insertFormat('> ', '', '引用文字')">
          <FileTextOutlined />
        </a-button>
      </a-tooltip>
      <a-divider type="vertical" />
      <a-tooltip title="代码块">
        <a-button type="text" size="small" @click="insertCodeBlock('python')">
          <CodeOutlined />
        </a-button>
      </a-tooltip>
      <a-tooltip title="行内代码">
        <a-button type="text" size="small" @click="insertInlineCode()">
          <FileTextOutlined />
        </a-button>
      </a-tooltip>
      <a-divider type="vertical" />
      <a-tooltip title="链接">
        <a-button type="text" size="small" @click="insertFormat('[', '](https://example.com)', '链接文字')">
          <LinkOutlined />
        </a-button>
      </a-tooltip>
      <a-tooltip title="图片">
        <a-button type="text" size="small" @click="openImageModal">
          <PictureOutlined />
        </a-button>
      </a-tooltip>
      <a-divider type="vertical" />
      <a-tooltip title="无序列表">
        <a-button type="text" size="small" @click="insertFormat('- ', '', '列表项')">
          <UnorderedListOutlined />
        </a-button>
      </a-tooltip>
      <a-tooltip title="有序列表">
        <a-button type="text" size="small" @click="insertFormat('1. ', '', '列表项')">
          <OrderedListOutlined />
        </a-button>
      </a-tooltip>
      <a-divider type="vertical" />
      <a-tooltip title="分割线">
        <a-button type="text" size="small" @click="insertFormat('\n---\n', '')">
          <MinusOutlined />
        </a-button>
      </a-tooltip>
      <div class="toolbar-right">
        <a-button
          type="text"
          size="small"
          :class="{ active: previewMode === 'split' }"
          @click="previewMode = 'split'"
        >
          <ColumnWidthOutlined /> 分屏
        </a-button>
        <a-button
          type="text"
          size="small"
          :class="{ active: previewMode === 'edit' }"
          @click="previewMode = 'edit'"
        >
          <EditOutlined /> 编辑
        </a-button>
        <a-button
          type="text"
          size="small"
          :class="{ active: previewMode === 'preview' }"
          @click="previewMode = 'preview'"
        >
          <EyeOutlined /> 预览
        </a-button>
      </div>
    </div>

    <!-- 编辑器主体 -->
    <div class="editor-container" :class="'mode-' + previewMode">
      <!-- 编辑区 -->
      <div class="editor-main" v-show="previewMode !== 'preview'">
        <textarea
          ref="editorRef"
          v-model="article.content"
          placeholder="开始写作... 支持 Markdown 格式

快捷键：
- 输入 ```python 回车 自动创建代码块
- 输入 ```javascript 回车 自动创建代码块
- Ctrl+B 粗体  Ctrl+I 斜体"
          class="content-editor"
          @keydown="handleKeydown"
          @blur="saveSelection"
        />
      </div>

      <!-- 预览区 -->
      <div class="editor-preview" v-show="previewMode !== 'edit'">
        <div class="preview-header">
          <span>预览</span>
          <span class="word-count">{{ wordCount }} 字</span>
        </div>
        <div class="preview-content" v-html="renderedContent"></div>
      </div>

      <!-- AI 侧边栏 -->
      <div class="editor-sidebar" v-if="showAiAssistant">
        <div class="ai-panel">
          <div class="ai-header">
            <h3><RobotOutlined /> AI写作助手</h3>
            <a-button type="text" size="small" @click="showAiAssistant = false">
              <CloseOutlined />
            </a-button>
          </div>
          <div class="ai-content">
            <div class="ai-actions">
              <a-button size="small" :loading="aiLoading" @click="aiAssist('continue')">续写</a-button>
              <a-button size="small" :loading="aiLoading" @click="aiAssist('polish')">润色</a-button>
              <a-button size="small" :loading="aiLoading" @click="aiAssist('expand')">扩写</a-button>
              <a-button size="small" :loading="aiLoading" @click="aiAssist('title')">生成标题</a-button>
            </div>
            <a-divider />
            <div class="ai-chat">
              <div class="chat-messages">
                <div v-for="(msg, index) in aiMessages" :key="index" :class="['message', msg.role]">
                  <div class="message-content">{{ msg.content }}</div>
                  <div v-if="msg.role === 'ai' && index > 0" class="message-actions">
                    <a-button type="link" size="small" @click="insertToEditor(msg.content)">
                      <EditOutlined /> 插入编辑器
                    </a-button>
                  </div>
                </div>
              </div>
              <a-input
                v-model:value="aiInput"
                placeholder="输入消息..."
                @pressEnter="sendAiMessage"
              >
                <template #suffix>
                  <SendOutlined @click="sendAiMessage" />
                </template>
              </a-input>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片上传弹窗 -->
    <a-modal
      v-model:open="imageModalVisible"
      title="插入图片"
      ok-text="插入"
      cancel-text="取消"
      @ok="confirmInsertImage"
      @cancel="closeImageModal"
    >
      <a-form layout="vertical">
        <a-form-item label="图片地址">
          <a-input
            v-model:value="imageModalUrl"
            placeholder="粘贴网络图片链接，或点击下方上传本地图片..."
            allow-clear
          />
        </a-form-item>
        <a-form-item>
          <a-upload
            :show-upload-list="false"
            :before-upload="beforeContentImageUpload"
            :custom-request="handleContentImageUpload"
            accept="image/*"
          >
            <a-button :loading="contentImageUploading">
              <UploadOutlined /> 上传本地图片
            </a-button>
          </a-upload>
          <div v-if="imageModalUrl" class="image-preview-wrap">
            <img :src="getImageUrl(imageModalUrl)" class="image-preview" />
          </div>
        </a-form-item>
        <a-form-item label="图片对齐方式">
          <a-radio-group v-model:value="imageModalAlign">
            <a-radio-button value="left">左对齐</a-radio-button>
            <a-radio-button value="center">居中</a-radio-button>
            <a-radio-button value="right">右对齐</a-radio-button>
          </a-radio-group>
        </a-form-item>
        <a-form-item label="图片描述（alt）">
          <a-input v-model:value="imageModalAlt" placeholder="输入图片描述..." />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  RobotOutlined, CloseOutlined, SendOutlined,
  BoldOutlined, ItalicOutlined, FontSizeOutlined,
  CodeOutlined, FileTextOutlined, LinkOutlined, PictureOutlined,
  UnorderedListOutlined, OrderedListOutlined, MinusOutlined,
  ColumnWidthOutlined, EditOutlined, EyeOutlined, UploadOutlined
} from '@ant-design/icons-vue'
import { createArticle, updateArticle, getArticle } from '@/api/article'
import { getCategories } from '@/api/category'
import { getTags } from '@/api/tag'
import { uploadImage } from '@/api/upload'
import { aiAssist as apiAiAssist, aiChat } from '@/api/ai'
import { useUserStore } from '@/stores/user'
import { getImageUrl } from '@/utils/image'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const route = useRoute()
const router = useRouter()
const editorRef = ref(null)
const userStore = useUserStore()

const article = reactive({
  id: null,
  title: '',
  content: '',
  summary: '',
  cover_image: '',
  category_id: null,
  tag_ids: [],
  status: 0,
  needs_reapproval: false
})

const categories = ref([])
const tags = ref([])
const saving = ref(false)
const coverUploading = ref(false)
const showAiAssistant = ref(false)
const aiInput = ref('')
const aiSessionKey = computed(() => `ai_chat_${userStore.user?.id || 'guest'}_${route.params.id || 'new'}`)
const aiMessages = ref([
  { role: 'ai', content: '你好！我是AI写作助手，可以帮助你续写、润色、扩写笔记。' }
])
const previewMode = ref('split')
const savedSelection = ref({ start: 0, end: 0 })

// 从 sessionStorage 恢复 AI 对话
const loadAiMessages = () => {
  try {
    const saved = sessionStorage.getItem(aiSessionKey)
    if (saved) {
      aiMessages.value = JSON.parse(saved)
    }
  } catch (e) {
    // ignore
  }
}

// 保存 AI 对话到 sessionStorage
watch(aiMessages, (val) => {
  try {
    sessionStorage.setItem(aiSessionKey, JSON.stringify(val))
  } catch (e) {
    // ignore
  }
}, { deep: true })

// 图片上传弹窗状态
const imageModalVisible = ref(false)
const imageModalUrl = ref('')
const imageModalAlt = ref('')
const imageModalAlign = ref('center')
const contentImageUploading = ref(false)

// 初始化 Markdown 渲染器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        const highlighted = hljs.highlight(str, { language: lang }).value
        return `<pre class="hljs"><div class="code-header"><span class="code-lang">${lang}</span><span class="code-copy">复制</span></div><code class="language-${lang}">${highlighted}</code></pre>`
      } catch (__) {}
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
  }
})

// 渲染后的内容
const renderedContent = computed(() => {
  return md.render(article.content || '')
})

// 字数统计
const wordCount = computed(() => {
  return article.content.length
})

// 获取分类和标签
const fetchMetaData = async () => {
  try {
    const [catRes, tagRes] = await Promise.all([
      getCategories(),
      getTags()
    ])
    if (catRes.code === 200) {
      categories.value = Array.isArray(catRes.data) ? catRes.data : (catRes.data?.items || [])
    }
    if (tagRes.code === 200) {
      tags.value = Array.isArray(tagRes.data) ? tagRes.data : (tagRes.data?.items || [])
    }
  } catch (error) {
    console.error('获取元数据失败:', error)
  }
}

// 保存光标位置
const saveSelection = () => {
  const textarea = editorRef.value
  if (textarea) {
    savedSelection.value = {
      start: textarea.selectionStart,
      end: textarea.selectionEnd
    }
  }
}

// 插入格式
const insertFormat = (before, after, placeholder = '') => {
  if (previewMode.value === 'preview') {
    previewMode.value = 'split'
    return
  }

  const textarea = editorRef.value
  if (!textarea) {
    message.warning('请切换到编辑模式')
    return
  }

  const start = savedSelection.value.start
  const end = savedSelection.value.end
  let selected = article.content.substring(start, end)

  // 如果没有选中文字，使用占位文字
  if (!selected && placeholder) {
    selected = placeholder
  }

  const insertText = before + selected + after
  const newContent = article.content.substring(0, start) + insertText + article.content.substring(end)

  // 更新内容（直接赋值触发响应式）
  article.content = newContent

  // 等 Vue 更新 DOM 后再聚焦和设置光标
  nextTick(() => {
    textarea.focus()
    const cursorPos = start + before.length
    textarea.setSelectionRange(cursorPos, cursorPos + selected.length)
  })
}

// 插入代码块
const insertCodeBlock = (lang) => {
  const before = '```' + lang + '\n'
  const after = '\n```'
  insertFormat(before, after, 'print("Hello World")')
}

// 插入行内代码
const insertInlineCode = () => {
  insertFormat('`', '`', 'code')
}

// 处理键盘事件
const handleKeydown = (e) => {
  const textarea = editorRef.value
  const start = textarea.selectionStart
  const text = article.content

  // 检测 ```language + Enter 快捷输入
  if (e.key === 'Enter') {
    const lineStart = text.lastIndexOf('\n', start - 1) + 1
    const currentLine = text.substring(lineStart, start)
    const codeMatch = currentLine.match(/^```(\w*)$/)

    if (codeMatch) {
      e.preventDefault()
      const lang = codeMatch[1] || ''
      const before = text.substring(0, start)
      const after = text.substring(start)
      const insertText = `\n\n${after.startsWith('\n') ? '' : '\n'}\`\`\``
      article.content = before + insertText + after

      nextTick(() => {
        const newPos = before.length + 1
        textarea.setSelectionRange(newPos, newPos)
        textarea.focus()
      })
      return
    }
  }

  // Ctrl+B 粗体
  if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
    e.preventDefault()
    insertFormat('**', '**')
    return
  }

  // Ctrl+I 斜体
  if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
    e.preventDefault()
    insertFormat('*', '*')
    return
  }
}

// 封面上传前校验
const beforeCoverUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

// 封面上传
const handleCoverUpload = async ({ file }) => {
  coverUploading.value = true
  try {
    const res = await uploadImage(file, 1)
    if (res.code === 200) {
      article.cover_image = res.data.url
      message.success('封面上传成功')
    } else {
      message.error(res.message || '上传失败')
    }
  } catch (error) {
    message.error(error.message || '上传失败')
  } finally {
    coverUploading.value = false
  }
}

// ========== 内容图片上传弹窗 ==========
const openImageModal = () => {
  imageModalVisible.value = true
  imageModalUrl.value = ''
  imageModalAlt.value = ''
  imageModalAlign.value = 'center'
  contentImageUploading.value = false
}

const closeImageModal = () => {
  imageModalVisible.value = false
  imageModalUrl.value = ''
  imageModalAlt.value = ''
  imageModalAlign.value = 'center'
}

const beforeContentImageUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('只能上传图片文件')
    return false
  }
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('图片大小不能超过 10MB')
    return false
  }
  return true
}

const handleContentImageUpload = async ({ file }) => {
  contentImageUploading.value = true
  try {
    const res = await uploadImage(file, 2)
    if (res.code === 200) {
      imageModalUrl.value = res.data.url
      message.success('图片上传成功')
    } else {
      message.error(res.message || '上传失败')
    }
  } catch (error) {
    message.error(error.message || '上传失败')
  } finally {
    contentImageUploading.value = false
  }
}

const confirmInsertImage = () => {
  if (!imageModalUrl.value) {
    message.error('请先上传图片')
    return
  }
  const alt = imageModalAlt.value.trim() || '图片'
  const url = imageModalUrl.value
  let insertText = ''
  if (imageModalAlign.value === 'left') {
    insertText = `<img src="${url}" alt="${alt}" style="display:block;margin:8px auto 8px 0;max-width:100%;border-radius:8px;">`
  } else if (imageModalAlign.value === 'right') {
    insertText = `<img src="${url}" alt="${alt}" style="display:block;margin:8px 0 8px auto;max-width:100%;border-radius:8px;">`
  } else {
    // 居中（默认）
    insertText = `<img src="${url}" alt="${alt}" style="display:block;margin:8px auto;max-width:100%;border-radius:8px;">`
  }
  insertFormat('\n' + insertText + '\n', '', '')
  closeImageModal()
}

const saveArticle = async () => {
  if (!article.title.trim()) {
    message.error('请输入标题')
    return
  }
  if (!article.category_id) {
    message.error('请选择分类')
    return
  }
  if (!article.content.trim()) {
    message.error('请输入内容')
    return
  }
  saving.value = true
  try {
    const data = {
      title: article.title,
      content: article.content,
      summary: article.summary || article.content.slice(0, 200),
      cover_image: article.cover_image || null,
      content_type: 1,
      category_id: article.category_id || null,
      tag_ids: article.tag_ids || [],
      status: 1
    }

    let res
    if (article.id) {
      res = await updateArticle(article.id, data)
    } else {
      res = await createArticle(data)
    }

    if (res.code === 200) {
      if (article.needs_reapproval && article.id) {
        message.success('已提交发布申请，等待管理员审核')
      } else {
        message.success(article.id ? '更新成功' : '发布成功')
      }
      router.push('/user/articles')
    }
  } catch (error) {
    message.error(error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const aiLoading = ref(false)

const aiAssist = async (action) => {
  const content = article.content || article.title || ''
  if (!content.trim()) {
    message.warning('请先输入一些内容')
    return
  }
  aiLoading.value = true
  aiMessages.value.push({
    role: 'user',
    content: `请帮我${action === 'continue' ? '续写' : action === 'polish' ? '润色' : action === 'expand' ? '扩写' : '生成标题'}`
  })
  try {
    const res = await apiAiAssist({ action, content, context: article.title })
    if (res.code === 200) {
      const result = res.data.result
      aiMessages.value.push({ role: 'ai', content: result })
      // 续写/润色/扩写时自动插入到编辑器
      if (action === 'continue' || action === 'expand') {
        article.content += '\n\n' + result
      } else if (action === 'polish') {
        // 润色替换选中的内容或全文
        if (savedSelection.value.start !== savedSelection.value.end) {
          const before = article.content.substring(0, savedSelection.value.start)
          const after = article.content.substring(savedSelection.value.end)
          article.content = before + result + after
        } else {
          article.content = result
        }
      } else if (action === 'title' && !article.title) {
        article.title = result.split('\n')[0].replace(/^\d+\.\s*/, '').trim()
      }
    }
  } catch (error) {
    message.error(error.message || 'AI处理失败')
    aiMessages.value.push({ role: 'ai', content: '抱歉，AI处理失败，请稍后重试。' })
  } finally {
    aiLoading.value = false
  }
}

const sendAiMessage = async () => {
  if (!aiInput.value.trim() || aiLoading.value) return
  const userMsg = aiInput.value.trim()
  aiMessages.value.push({ role: 'user', content: userMsg })
  aiInput.value = ''
  aiLoading.value = true
  try {
    const res = await aiChat({
      message: userMsg,
      context_type: 'article',
      context_content: article.content?.substring(0, 500) || ''
    })
    if (res.code === 200) {
      aiMessages.value.push({ role: 'ai', content: res.data.reply })
    }
  } catch (error) {
    message.error(error.message || 'AI对话失败')
    aiMessages.value.push({ role: 'ai', content: '抱歉，AI对话失败，请稍后重试。' })
  } finally {
    aiLoading.value = false
  }
}

const insertToEditor = (text) => {
  const textarea = editorRef.value
  if (!textarea) return
  const start = textarea.selectionStart || 0
  const end = textarea.selectionEnd || 0
  const before = article.content.substring(0, start)
  const after = article.content.substring(end)
  article.content = before + text + after
  nextTick(() => {
    textarea.selectionStart = textarea.selectionEnd = start + text.length
    textarea.focus()
  })
}

onMounted(() => {
  fetchMetaData()
  loadAiMessages()
  const articleId = route.params.id
  if (articleId) {
    getArticle(articleId).then(res => {
      if (res.code === 200) {
        Object.assign(article, res.data)
      }
    })
    return
  }
  // 从 MD 导入的草稿
  if (route.query.from === 'md') {
    try {
      const raw = sessionStorage.getItem('md_import_draft')
      if (raw) {
        const draft = JSON.parse(raw)
        if (draft.title) article.title = draft.title
        if (draft.content) article.content = draft.content
        sessionStorage.removeItem('md_import_draft')
        message.success('已导入 MD 内容，可编辑后预览发布')
      }
    } catch (e) {
      // ignore
    }
  }
})
</script>

<style scoped lang="less">
.editor-page {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

// 顶部工具栏
.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
  gap: 16px;

  .title-input {
    flex: 1;
    font-size: 20px;
    font-weight: 600;
    border: none;
    background: transparent;

    &:focus {
      box-shadow: none;
    }
  }

  .toolbar-meta {
    display: flex;
    gap: 12px;
    align-items: center;

    .cover-uploader {
      display: flex;
      align-items: center;
      gap: 8px;

      .ant-input {
        background: var(--bg-secondary);
      }
    }
  }

  .toolbar-actions {
    display: flex;
    gap: 12px;
  }

  @media (max-width: 768px) {
    flex-wrap: wrap;
    padding: 12px 16px;

    .toolbar-meta {
      width: 100%;
      order: 3;
      flex-wrap: wrap;

      .cover-uploader {
        width: 100%;

        .ant-input {
          flex: 1;
        }
      }
    }
  }
}

// Markdown 工具栏
.markdown-toolbar {
  display: flex;
  align-items: center;
  padding: 8px 24px;
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-secondary);
  gap: 4px;

  .ant-btn {
    color: var(--text-secondary);

    &:hover {
      color: var(--ant-primary-color);
      background: var(--bg-tertiary);
    }

    &.active {
      color: var(--ant-primary-color);
      background: rgba(24, 144, 255, 0.1);
    }
  }

  .toolbar-right {
    margin-left: auto;
    display: flex;
    gap: 4px;
  }

  @media (max-width: 768px) {
    padding: 8px 16px;
    overflow-x: auto;

    .toolbar-right {
      display: none;
    }
  }
}

// 编辑器容器
.editor-container {
  flex: 1;
  display: flex;
  overflow: hidden;

  &.mode-edit {
    .editor-main {
      flex: 1;
    }
    .editor-preview {
      display: none;
    }
  }

  &.mode-preview {
    .editor-main {
      display: none;
    }
    .editor-preview {
      flex: 1;
    }
  }

  &.mode-split {
    .editor-main {
      flex: 1;
    }
    .editor-preview {
      flex: 1;
      border-left: 1px solid var(--border-color);
    }
  }
}

// 编辑区
.editor-main {
  padding: 24px;
  overflow-y: auto;

  .content-editor {
    width: 100%;
    min-height: 100%;
    border: none;
    resize: none;
    font-size: 15px;
    line-height: 1.8;
    background: transparent;
    color: var(--text-primary);
    font-family: 'Menlo', 'Monaco', 'Courier New', monospace;

    &:focus {
      outline: none;
    }

    &::placeholder {
      color: var(--text-tertiary);
    }
  }

  @media (max-width: 768px) {
    padding: 16px;
  }
}

// 预览区
.editor-preview {
  padding: 24px;
  overflow-y: auto;
  background: var(--bg-primary);

  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-secondary);
    font-size: 13px;

    .word-count {
      font-size: 12px;
    }
  }

  .preview-content {
    color: var(--text-primary);
    line-height: 1.8;

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

    :deep(pre.hljs) {
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

        .code-copy {
          font-size: 12px;
          color: #858585;
          cursor: pointer;

          &:hover {
            color: #fff;
          }
        }
      }

      code {
        display: block;
        padding: 16px;
        overflow-x: auto;
        background: transparent;
      }
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

  @media (max-width: 768px) {
    padding: 16px;
  }
}

// AI 侧边栏
.editor-sidebar {
  width: 360px;
  border-left: 1px solid var(--border-color);
  background: var(--bg-secondary);

  @media (max-width: 768px) {
    position: fixed;
    top: 64px;
    right: 0;
    bottom: 0;
    width: 100%;
    z-index: 100;
  }
}

.ai-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color);

  h3 {
    margin: 0;
  }
}

.ai-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.ai-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ai-chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-top: 16px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 16px;

  .message {
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 8px;
    max-width: 90%;

    .message-content {
      white-space: pre-wrap;
      word-break: break-word;
    }

    .message-actions {
      margin-top: 4px;
      text-align: right;

      .ant-btn {
        font-size: 12px;
        padding: 0;
        height: auto;
      }
    }

    &.user {
      background: var(--ant-primary-color);
      color: white;
      margin-left: auto;
    }

    &.ai {
      background: var(--bg-tertiary);
      color: var(--text-primary);
    }
  }
}

// 图片弹窗预览
.image-preview-wrap {
  margin-top: 12px;
  padding: 8px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px dashed var(--border-color);
  text-align: center;

  .image-preview {
    max-width: 100%;
    max-height: 200px;
    border-radius: 4px;
    object-fit: contain;
  }
}
</style>
