<template>
  <div>
    <h1>评论管理</h1>
    <a-table :columns="columns" :data-source="comments" :loading="loading" rowKey="id" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="statusColor(record.status)">
            {{ statusLabel(record.status) }}
          </a-tag>
        </template>
        <template v-if="column.key === 'created_at'">
          {{ formatDateTime(record.created_at) }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button v-if="record.status === 0" type="text" @click="handleReview(record)">通过</a-button>
            <a-button v-if="record.status !== 2" type="text" danger @click="openRetractModal(record)">撤回</a-button>
            <a-button type="text" danger @click="deleteComment(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="retractModalVisible"
      title="撤回评论"
      ok-text="确认撤回"
      ok-type="danger"
      @ok="confirmRetract"
      @cancel="closeRetractModal"
    >
      <a-form layout="vertical">
        <a-form-item label="撤回原因">
          <a-textarea v-model:value="retractReason" :rows="3" placeholder="请输入撤回原因..." />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { getAdminComments, reviewComment, deleteComment as deleteCommentApi } from '@/api/admin'
import { formatDateTime } from '@/utils/date'

const loading = ref(false)
const comments = ref([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const retractModalVisible = ref(false)
const retractReason = ref('违反规定')
const retractTarget = ref(null)

const columns = [
  { title: '内容', dataIndex: 'content', key: 'content', ellipsis: true },
  { title: '用户', dataIndex: ['user', 'username'], key: 'user' },
  { title: '笔记', dataIndex: ['article', 'title'], key: 'article' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '发布时间', dataIndex: 'created_at', key: 'created_at' },
  { title: '操作', key: 'action', fixed: 'right', width: 200 }
]

const statusLabel = (status) => {
  if (status === 1) return '已通过'
  if (status === 2) return '已撤回'
  return '待审核'
}

const statusColor = (status) => {
  if (status === 1) return 'success'
  if (status === 2) return 'error'
  return 'warning'
}

const fetchComments = async () => {
  loading.value = true
  try {
    const res = await getAdminComments({
      page: page.value,
      size: pageSize.value
    })
    if (res.code === 200) {
      comments.value = res.data.items
      total.value = res.data.total
    }
  } catch (error) {
    message.error('获取评论列表失败')
  } finally {
    loading.value = false
  }
}

const handleReview = async (record) => {
  try {
    const res = await reviewComment(record.id, 1)
    if (res.code === 200) {
      message.success('审核通过')
      fetchComments()
    }
  } catch (error) {
    message.error('审核失败')
  }
}

const openRetractModal = (record) => {
  retractTarget.value = record
  retractReason.value = '违反规定'
  retractModalVisible.value = true
}

const closeRetractModal = () => {
  retractTarget.value = null
  retractModalVisible.value = false
}

const confirmRetract = async () => {
  if (!retractTarget.value) return
  try {
    const res = await reviewComment(retractTarget.value.id, 2, retractReason.value)
    if (res.code === 200) {
      message.success('已撤回并通知用户')
      closeRetractModal()
      fetchComments()
    }
  } catch (error) {
    message.error('撤回失败')
  }
}

const deleteComment = async (record) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这条评论吗？删除后不可恢复。',
    okText: '删除',
    okType: 'danger',
    onOk: async () => {
      try {
        const res = await deleteCommentApi(record.id)
        if (res.code === 200) {
          message.success('删除成功')
          fetchComments()
        }
      } catch (error) {
        message.error('删除失败')
      }
    }
  })
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped lang="less">
:deep(.ant-table-cell-fix-right),
:deep(.ant-table-cell-fix-right-first) {
  background: transparent !important;
}
</style>
