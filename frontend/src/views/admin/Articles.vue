<template>
  <div>
    <div class="page-header">
      <h1>笔记管理</h1>
      <a-space>
        <a-input-search
          v-model:value="keyword"
          placeholder="搜索标题..."
          style="width: 220px"
          allow-clear
          @search="handleSearch"
        />
        <a-upload
          :show-upload-list="false"
          :before-upload="handleMdUpload"
          accept=".md,.markdown,text/markdown"
        >
          <a-button>
            <UploadOutlined /> 上传 MD 文件
          </a-button>
        </a-upload>
        <a-button type="primary" @click="goToEditor">
          <PlusOutlined /> 新建笔记
        </a-button>
      </a-space>
    </div>

    <a-tabs v-model:activeKey="activeStatus" @change="handleStatusChange">
      <a-tab-pane key="all" tab="全部" />
      <a-tab-pane key="0" tab="待审核 / 草稿" />
      <a-tab-pane key="1" tab="已发布" />
      <a-tab-pane key="2" tab="已下架" />
    </a-tabs>

    <a-table
      :columns="columns"
      :data-source="articles"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      row-key="id"
      :scroll="{ x: 1000 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'title'">
          <a @click="viewArticle(record)" class="title-link">{{ record.title }}</a>
        </template>
        <template v-if="column.key === 'author'">
          {{ record.author?.nickname || record.author?.username || '-' }}
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="statusColor(record)">{{ statusLabel(record) }}</a-tag>
        </template>
        <template v-if="column.key === 'created_at'">
          {{ formatDate(record.created_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" size="small" @click="editArticle(record)">编辑</a-button>
            <a-button v-if="record.slug" type="text" size="small" @click="viewArticle(record)">预览</a-button>
            <a-button v-if="record.status === 0" type="text" size="small" @click="handleReview(record, 1)">通过</a-button>
            <a-button v-if="record.status === 1" type="text" size="small" @click="openTakedownModal(record)">下架</a-button>
            <a-button type="text" size="small" @click="handleExport(record)"><DownloadOutlined /> 导出</a-button>
            <a-button type="text" size="small" danger @click="confirmDelete(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 下架确认弹窗 -->
    <a-modal
      v-model:open="takedownModalVisible"
      title="确认下架该笔记"
      ok-text="下架"
      :ok-button-props="{ danger: true }"
      cancel-text="取消"
      @ok="confirmTakedown"
      @cancel="takedownModalVisible = false"
    >
      <p class="modal-desc">下架后读者将无法访问，作者会收到通知。</p>
      <a-form layout="vertical">
        <a-form-item label="下架原因">
          <a-textarea
            v-model:value="takedownReason"
            :rows="3"
            placeholder="请输入下架原因..."
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  UploadOutlined,
  PlusOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'
import {
  getAllArticles,
  reviewArticle as reviewArticleApi,
  deleteArticle as deleteArticleApi
} from '@/api/admin'
import { exportArticleMd } from '@/api/article'
import { formatDateTime } from '@/utils/date'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const keyword = ref('')
const activeStatus = ref('all')
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

// 下架弹窗状态
const takedownModalVisible = ref(false)
const takedownReason = ref('违反笔记规则')
const takedownRecord = ref(null)

const columns = [
  { title: '标题', key: 'title', ellipsis: true },
  { title: '作者', key: 'author', width: 140 },
  { title: '状态', key: 'status', width: 110 },
  { title: '阅读量', dataIndex: 'view_count', key: 'view_count', width: 100 },
  { title: '创建时间', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 260 }
]

const statusLabel = (r) => {
  if (r.status === 1) return '已发布'
  if (r.status === 2) return '已下架'
  if (r.status === 0 && r.needs_reapproval) return '待审核'
  return '草稿'
}
const statusColor = (r) => {
  if (r.status === 1) return 'success'
  if (r.status === 2) return 'error'
  if (r.status === 0 && r.needs_reapproval) return 'warning'
  return 'default'
}
const formatDate = (d) => formatDateTime(d)

const fetchArticles = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      size: pagination.value.pageSize
    }
    if (keyword.value) params.keyword = keyword.value
    if (activeStatus.value !== 'all') params.status = Number(activeStatus.value)
    const res = await getAllArticles(params)
    if (res.code === 200) {
      articles.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (e) {
    message.error('获取笔记列表失败')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  fetchArticles()
}

const handleSearch = () => {
  pagination.value.current = 1
  fetchArticles()
}

const handleStatusChange = () => {
  pagination.value.current = 1
  fetchArticles()
}

const viewArticle = (record) => {
  if (record.slug) {
    window.open(`/article/${record.slug}`, '_blank')
  }
}

const editArticle = (record) => {
  if (record.slug) {
    router.push(`/editor/${record.slug}`)
  } else {
    message.error('该笔记没有有效的链接')
  }
}

const goToEditor = () => {
  router.push('/editor')
}

const handleReview = async (record, status, reason) => {
  try {
    const res = await reviewArticleApi(record.id, status, reason)
    if (res.code === 200) {
      message.success(status === 1 ? '已通过' : '已下架')
      fetchArticles()
    }
  } catch (e) {
    message.error('操作失败')
  }
}

const deleteArticle = async (record) => {
  try {
    const res = await deleteArticleApi(record.id)
    if (res.code === 200) {
      message.success('删除成功')
      fetchArticles()
    }
  } catch (e) {
    message.error('删除失败')
  }
}

const handleAction = (key, record) => {
  if (key === 'edit') return editArticle(record)
  if (key === 'view') return viewArticle(record)
  if (key === 'approve') return handleReview(record, 1)
  if (key === 'unpublish') {
    takedownRecord.value = record
    takedownReason.value = '违反笔记规则'
    takedownModalVisible.value = true
    return
  }
  if (key === 'delete') {
    Modal.confirm({
      title: '确认删除这篇笔记？',
      content: '删除后不可恢复。',
      okText: '删除',
      okType: 'danger',
      onOk: () => deleteArticle(record)
    })
  }
}

const confirmTakedown = async () => {
  if (!takedownRecord.value) return
  if (!takedownReason.value.trim()) {
    message.error('请填写下架原因')
    return
  }
  await handleReview(takedownRecord.value, 2, takedownReason.value.trim())
  takedownModalVisible.value = false
  takedownRecord.value = null
}

const openTakedownModal = (record) => {
  takedownRecord.value = record
  takedownReason.value = '违反笔记规则'
  takedownModalVisible.value = true
}

const confirmDelete = (record) => {
  Modal.confirm({
    title: '确认删除这篇笔记？',
    content: '删除后不可恢复。',
    okText: '删除',
    okType: 'danger',
    onOk: () => deleteArticle(record)
  })
}

const handleExport = async (record) => {
  try {
    const res = await exportArticleMd(record.id)
    const url = window.URL.createObjectURL(res)
    const link = document.createElement('a')
    link.href = url
    const safeTitle = (record.title || 'article').replace(/[\\/:*?"<>|]/g, '_')
    link.download = `${safeTitle}.md`
    link.click()
    window.URL.revokeObjectURL(url)
    message.success('导出成功')
  } catch (error) {
    message.error('导出失败')
  }
}

// ========== MD 文件上传解析 ==========
const parseMdFile = (text, filename) => {
  let title = ''
  let content = text
  // 兼容 YAML front-matter
  const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n?/)
  if (fmMatch) {
    const fm = fmMatch[1]
    const titleMatch = fm.match(/^title\s*:\s*(.+)$/m)
    if (titleMatch) title = titleMatch[1].trim().replace(/^["']|["']$/g, '')
    content = text.slice(fmMatch[0].length)
  }
  // 无标题时用第一行 # 标题
  if (!title) {
    const h1Match = content.match(/^#\s+(.+)$/m)
    if (h1Match) {
      title = h1Match[1].trim()
      // 移除第一行 h1
      content = content.replace(/^#\s+.+(\r?\n)?/, '')
    }
  }
  // 最后用文件名兜底
  if (!title) {
    title = filename.replace(/\.(md|markdown)$/i, '')
  }
  return { title, content: content.trim() }
}

const handleMdUpload = (file) => {
  const isMd = /\.(md|markdown)$/i.test(file.name)
  if (!isMd) {
    message.error('仅支持 .md / .markdown 文件')
    return false
  }
  if (file.size > 5 * 1024 * 1024) {
    message.error('文件大小不能超过 5MB')
    return false
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    const text = e.target?.result || ''
    const { title, content } = parseMdFile(String(text), file.name)
    // 通过 sessionStorage 传递给编辑器
    sessionStorage.setItem(
      'md_import_draft',
      JSON.stringify({ title, content, from: 'md', ts: Date.now() })
    )
    message.success('MD 文件已解析，进入编辑器预览与发布')
    router.push({ path: '/editor', query: { from: 'md' } })
  }
  reader.onerror = () => message.error('文件读取失败')
  reader.readAsText(file, 'utf-8')
  return false // 阻止默认上传
}

onMounted(() => {
  fetchArticles()
})
</script>

<style scoped lang="less">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;

  h1 {
    font-weight: 600;
    margin: 0;
  }
}

.title-link {
  color: var(--ant-primary-color);
  &:hover {
    text-decoration: underline;
  }
}

.action-trigger {
  color: var(--text-secondary);
  padding: 0 8px;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  &:hover {
    color: var(--ant-primary-color);
    background: var(--bg-secondary) !important;
  }
}

:deep(.menu-danger) {
  color: #ff4d4f;
  &:hover {
    background: rgba(255, 77, 79, 0.08);
  }
}

:deep(.ant-table-cell-fix-right) {
  background: transparent !important;
}
:deep(.ant-table-cell-fix-right-first) {
  background: transparent !important;
}

:deep(.ant-dropdown-menu) {
  background: var(--card-bg) !important;
  box-shadow: 0 3px 6px -4px rgba(0,0,0,0.48), 0 6px 16px 0 rgba(0,0,0,0.32), 0 9px 28px 8px rgba(0,0,0,0.2) !important;
}
:deep(.ant-dropdown-menu-item) {
  color: var(--text-primary) !important;
}
:deep(.ant-dropdown-menu-item:hover) {
  background: var(--bg-secondary) !important;
}
:deep(.ant-dropdown-menu-item-divider) {
  background: var(--border-color) !important;
}

.modal-desc {
  color: var(--text-secondary);
  margin-bottom: 16px;
}
</style>
