<template>
  <div class="page-container">
    <div class="page-header">
      <h1>我的笔记</h1>
      <a-input-search
        v-model:value="searchKeyword"
        placeholder="搜索笔记标题..."
        enter-button
        allow-clear
        class="search-input"
        @search="handleSearch"
      />
    </div>

    <a-table :columns="columns" :data-source="articles" :loading="loading">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'cover_image'">
          <img v-if="record.cover_image" :src="getImageUrl(record.cover_image)" class="cover-thumb" />
          <span v-else>-</span>
        </template>
        <template v-if="column.key === 'status'">
          <a-tag :color="statusColor(record)">
            {{ statusLabel(record) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'published_at'">
          {{ formatDate(record.published_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" @click="editArticle(record)">编辑</a-button>
            <a-button type="text" @click="handleExport(record)"><DownloadOutlined /> 导出</a-button>
            <a-dropdown v-if="!record.needs_reapproval">
              <a-button type="text" size="small">
                修改状态 <DownOutlined />
              </a-button>
              <template #overlay>
                <a-menu @click="(e) => handleStatusChange(record, e.key)">
                  <a-menu-item key="1">
                    <a-tag color="success">已发布</a-tag>
                  </a-menu-item>
                  <a-menu-item key="0">
                    <a-tag color="default">草稿</a-tag>
                  </a-menu-item>
                  <a-menu-item key="2">
                    <a-tag color="error">已下架</a-tag>
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
            <a-button v-if="record.needs_reapproval && record.status !== 1" type="primary" size="small" @click="reapplyPublish(record)">
              重新申请
            </a-button>
            <a-button type="text" danger @click="deleteArticle(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import { getMyArticles, deleteArticle as deleteArticleApi, updateArticle, exportArticleMd } from '@/api/article'
import { formatDate } from '@/utils/date'
import { getImageUrl } from '@/utils/image'

const router = useRouter()
const loading = ref(false)
const articles = ref([])
const searchKeyword = ref('')

const columns = [
  { title: '封面', dataIndex: 'cover_image', key: 'cover_image', width: 80 },
  { title: '标题', dataIndex: 'title', key: 'title' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '阅读量', dataIndex: 'view_count', key: 'view_count' },
  { title: '发布时间', dataIndex: 'published_at', key: 'published_at' },
  { title: '操作', key: 'action' }
]

const fetchMyArticles = async (keyword = '') => {
  loading.value = true
  try {
    const res = await getMyArticles(keyword ? { keyword } : {})
    if (res.code === 200) {
      articles.value = res.data.items
    }
  } catch (error) {
    message.error('获取笔记列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = (value) => {
  fetchMyArticles(value)
}

// 监听输入变化，清空时自动重置
watch(searchKeyword, (newVal) => {
  if (newVal === '') {
    fetchMyArticles('')
  }
})

const editArticle = (record) => {
  router.push(`/editor/${record.slug}`)
}

const statusLabel = (record) => {
  if (record.status === 1) return '已发布'
  if (record.status === 2) return '已下架'
  if (record.needs_reapproval) return '待审核'
  return '草稿'
}

const statusColor = (record) => {
  if (record.status === 1) return 'success'
  if (record.status === 2) return 'error'
  if (record.needs_reapproval) return 'warning'
  return 'default'
}

const reapplyPublish = async (record) => {
  try {
    const res = await updateArticle(record.id, { status: 1 })
    if (res.code === 200) {
      message.success('已提交发布申请，等待管理员审核')
      fetchMyArticles()
    }
  } catch (error) {
    message.error('操作失败')
  }
}

const deleteArticle = async (record) => {
  try {
    const res = await deleteArticleApi(record.id)
    if (res.code === 200) {
      message.success('删除成功')
      fetchMyArticles()
    }
  } catch (error) {
    message.error('删除失败')
  }
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

const handleStatusChange = async (record, status) => {
  const statusMap = { '0': '草稿', '1': '已发布', '2': '已下架' }
  try {
    const res = await updateArticle(record.id, { status: Number(status) })
    if (res.code === 200) {
      message.success(`状态已更新为「${statusMap[status]}」`)
      fetchMyArticles()
    }
  } catch (error) {
    message.error('状态更新失败')
  }
}

onMounted(() => {
  fetchMyArticles()
})
</script>

<style scoped lang="less">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;

  h1 {
    margin: 0;
    flex-shrink: 0;
    font-size: 24px;
    font-weight: 600;
  }
}

.search-input {
  max-width: 320px;
  width: 100%;
}

.cover-thumb {
  width: 48px;
  height: 36px;
  object-fit: cover;
  border-radius: 4px;
}
</style>
