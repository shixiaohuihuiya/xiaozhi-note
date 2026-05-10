<template>
  <div>
    <div class="page-header">
      <h1>图片管理</h1>
      <a-upload
        :show-upload-list="false"
        :before-upload="beforeUpload"
        :custom-request="handleUpload"
        accept="image/*"
        multiple
      >
        <a-button type="primary" :loading="uploading">
          <UploadOutlined /> 上传图片
        </a-button>
      </a-upload>
    </div>

    <a-tabs v-model:activeKey="activeType" @change="handleTypeChange" class="image-tabs">
      <a-tab-pane key="all" tab="全部" />
      <a-tab-pane key="1" tab="笔记封面" />
      <a-tab-pane key="2" tab="笔记内容" />
      <a-tab-pane key="3" tab="用户头像" />
    </a-tabs>

    <a-table
      :columns="columns"
      :data-source="images"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      :scroll="{ x: 1000 }"
      row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'preview'">
          <img :src="record.url" class="image-preview" @click="previewImage(record.url)" />
        </template>
        <template v-if="column.key === 'file_size'">
          {{ record.file_size }} KB
        </template>
        <template v-if="column.key === 'usage_type'">
          <a-tag :color="usageColorMap[record.usage_type] || 'default'">
            {{ usageTypeMap[record.usage_type] || '其他' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'uploader'">
          <span v-if="record.uploader">
            {{ record.uploader.nickname || record.uploader.username }}
          </span>
          <span v-else>-</span>
        </template>
        <template v-if="column.key === 'url'">
          <span class="url-text">{{ record.url }}</span>
          <a-button type="text" size="small" class="action-text-btn" @click="copyUrl(record.url)">
            复制
          </a-button>
        </template>
        <template v-if="column.key === 'created_at'">
          {{ formatDateTime(record.created_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="text" size="small" @click="copyUrl(record.url)">复制</a-button>
            <a-button type="text" size="small" danger @click="confirmDelete(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-image
      :style="{ display: 'none' }"
      :preview="{
        visible: previewVisible,
        onVisibleChange: (visible) => previewVisible = visible,
      }"
      :src="previewUrl"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  UploadOutlined
} from '@ant-design/icons-vue'
import { getUploadedImages, deleteUpload } from '@/api/upload'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const uploading = ref(false)
const images = ref([])
const previewVisible = ref(false)
const previewUrl = ref('')
const activeType = ref('all')

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0
})

const usageTypeMap = {
  1: '笔记封面',
  2: '笔记内容',
  3: '用户头像'
}

const usageColorMap = {
  1: 'blue',
  2: 'green',
  3: 'purple'
}

const columns = [
  { title: '预览', key: 'preview', width: 100 },
  { title: '原文件名', dataIndex: 'original_name', key: 'original_name', ellipsis: true },
  { title: '大小', dataIndex: 'file_size', key: 'file_size', width: 100 },
  { title: '用途', dataIndex: 'usage_type', key: 'usage_type', width: 100 },
  { title: '上传者', key: 'uploader', width: 120 },
  { title: '链接', key: 'url', ellipsis: true },
  { title: '上传时间', dataIndex: 'created_at', key: 'created_at', width: 180 },
  { title: '操作', key: 'action', width: 120 }
]

const fetchImages = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.current,
      size: pagination.value.pageSize
    }
    if (activeType.value !== 'all') {
      params.usage_type = Number(activeType.value)
    }
    const res = await getUploadedImages(params)
    if (res.code === 200) {
      images.value = res.data.items || []
      pagination.value.total = res.data.total || 0
    }
  } catch (error) {
    message.error('获取图片列表失败')
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  pagination.value.current = 1
  fetchImages()
}

const handleTableChange = (pag) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  fetchImages()
}

const beforeUpload = (file) => {
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

const handleUpload = async ({ file }) => {
  uploading.value = true
  try {
    const { uploadImage } = await import('@/api/upload')
    const res = await uploadImage(file, 2)
    if (res.code === 200) {
      message.success('上传成功')
      fetchImages()
    } else {
      message.error(res.message || '上传失败')
    }
  } catch (error) {
    message.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

const deleteImage = async (record) => {
  try {
    const res = await deleteUpload(record.id)
    if (res.code === 200) {
      message.success('删除成功')
      fetchImages()
    }
  } catch (error) {
    message.error('删除失败')
  }
}

const handleAction = (key, record) => {
  if (key === 'copy') return copyUrl(record.url)
  if (key === 'delete') {
    Modal.confirm({
      title: '确认删除该图片？',
      content: '删除后不可恢复。',
      okText: '删除',
      okType: 'danger',
      onOk: () => deleteImage(record)
    })
  }
}

const confirmDelete = (record) => {
  Modal.confirm({
    title: '确认删除该图片？',
    content: '删除后不可恢复。',
    okText: '删除',
    okType: 'danger',
    onOk: () => deleteImage(record)
  })
}

const previewImage = (url) => {
  previewUrl.value = url
  previewVisible.value = true
}

const copyUrl = (url) => {
  navigator.clipboard.writeText(url).then(() => {
    message.success('链接已复制')
  }).catch(() => {
    message.error('复制失败')
  })
}

onMounted(() => {
  fetchImages()
})
</script>

<style scoped lang="less">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-weight: 600;
  }
}

.image-tabs {
  margin-bottom: 16px;
}

.image-preview {
  width: 60px;
  height: 45px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: scale(1.05);
  }
}

.url-text {
  color: var(--text-secondary);
  font-size: 12px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}

.action-text-btn {
  color: var(--text-secondary);
  background: transparent !important;
  border: none !important;
  padding: 0 4px;
  &:hover {
    color: var(--ant-primary-color);
    background: var(--bg-secondary) !important;
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
</style>
