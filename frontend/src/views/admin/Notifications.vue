<template>
  <div class="admin-notification-container">
    <a-row :gutter="[16, 16]">
      <!-- Statistics Cards -->
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <a-statistic title="通知总数" :value="stats.total_count" :precision="0">
            <template #prefix>
              <BellOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <a-statistic title="系统通知" :value="stats.system_count" :precision="0">
            <template #prefix>
              <NotificationOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card" :bordered="false">
          <a-statistic title="今日新增" :value="stats.today_count" :precision="0">
            <template #prefix>
              <PlusCircleOutlined />
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card send-card" :bordered="false" @click="showSendModal = true">
          <div class="send-action">
            <SendOutlined class="send-icon" />
            <span class="send-text">发送通知</span>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <!-- Filter and Table -->
    <a-card class="table-card" :bordered="false" style="margin-top: 16px;">
      <template #title>
        <div class="card-header">
          <span>通知管理</span>
        </div>
      </template>

      <!-- Filters -->
      <div class="filter-section">
        <a-space>
          <a-select
            v-model:value="filters.user_id"
            placeholder="选择用户"
            allowClear
            showSearch
            style="width: 200px"
            :options="userOptions"
            @change="handleFilterChange"
          >
            <template #suffixIcon>
              <UserOutlined />
            </template>
          </a-select>
          
          <a-select
            v-model:value="filters.notification_type"
            placeholder="通知类型"
            allowClear
            style="width: 150px"
            @change="handleFilterChange"
          >
            <a-select-option :value="4">系统公告</a-select-option>
            <a-select-option :value="5">管理员通知</a-select-option>
            <a-select-option :value="1">文章下架</a-select-option>
            <a-select-option :value="2">评论审核</a-select-option>
            <a-select-option :value="3">新评论</a-select-option>
          </a-select>

          <a-select
            v-model:value="filters.is_system"
            placeholder="来源类型"
            allowClear
            style="width: 120px"
            @change="handleFilterChange"
          >
            <a-select-option :value="true">系统发送</a-select-option>
            <a-select-option :value="false">自动触发</a-select-option>
          </a-select>

          <a-button @click="handleReset">
            <ReloadOutlined /> 重置
          </a-button>
        </a-space>
      </div>

      <!-- Table -->
      <a-table
        :columns="columns"
        :data-source="notifications"
        :loading="loading"
        :pagination="pagination"
        row-key="id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'type'">
            <a-tag :color="getTypeColor(record.type)">
              {{ getTypeName(record.type) }}
            </a-tag>
          </template>

          <template v-if="column.key === 'username'">
            <a-tag v-if="record.user_id === null" color="blue">全员</a-tag>
            <span v-else>{{ record.username }}</span>
          </template>

          <template v-if="column.key === 'is_system'">
            <a-tag :color="record.is_system ? 'green' : 'default'">
              {{ record.is_system ? '系统发送' : '自动触发' }}
            </a-tag>
          </template>

          <template v-if="column.key === 'is_read'">
            <a-tag :color="record.is_read ? 'default' : 'red'">
              {{ record.is_read ? '已读' : '未读' }}
            </a-tag>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="handleViewDetail(record)"
              >
                <EyeOutlined /> 查看
              </a-button>
              <a-popconfirm
                title="确定删除此通知？"
                ok-text="删除"
                cancel-text="取消"
                ok-type="danger"
                @confirm="handleDelete(record.id)"
              >
                <a-button type="link" size="small" danger>
                  <DeleteOutlined /> 删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Send Notification Modal -->
    <a-modal
      v-model:open="showSendModal"
      title="发送通知"
      width="700px"
      :confirm-loading="sending"
      @ok="handleSendNotification"
      @cancel="handleCancelSend"
    >
      <a-form
        :model="sendForm"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 20 }"
      >
        <a-form-item label="通知标题" required>
          <a-input
            v-model:value="sendForm.title"
            placeholder="请输入通知标题"
            :maxlength="200"
            show-count
          />
        </a-form-item>

        <a-form-item label="通知内容">
          <a-textarea
            v-model:value="sendForm.content"
            placeholder="请输入通知内容（可选）"
            :rows="4"
            :maxlength="1000"
            show-count
          />
        </a-form-item>

        <a-form-item label="通知类型" required>
          <a-radio-group v-model:value="sendForm.type">
            <a-radio :value="4">系统公告</a-radio>
            <a-radio :value="5">管理员通知</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="接收对象" required>
          <a-radio-group v-model:value="sendForm.target_type" @change="handleTargetTypeChange">
            <a-radio value="all">全员通知</a-radio>
            <a-radio value="specific">指定用户</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item
          v-if="sendForm.target_type === 'specific'"
          label="选择用户"
          required
        >
          <a-select
            v-model:value="sendForm.target_user_ids"
            mode="multiple"
            placeholder="请选择接收用户"
            showSearch
            :options="userOptions"
            :max-tag-count="3"
            style="width: 100%"
          />
          <div class="form-tip">可选择多个用户，留空则发送给所有用户</div>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- View Detail Modal -->
    <a-modal
      v-model:open="showDetailModal"
      title="通知详情"
      :footer="null"
      width="600px"
    >
      <a-descriptions bordered :column="1" v-if="currentNotification">
        <a-descriptions-item label="标题">
          {{ currentNotification.title }}
        </a-descriptions-item>
        <a-descriptions-item label="类型">
          <a-tag :color="getTypeColor(currentNotification.type)">
            {{ getTypeName(currentNotification.type) }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="接收者">
          <a-tag v-if="currentNotification.user_id === null" color="blue">全员</a-tag>
          <span v-else>{{ currentNotification.username }}</span>
        </a-descriptions-item>
        <a-descriptions-item label="发送者">
          {{ currentNotification.creator_name }}
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag :color="currentNotification.is_read ? 'default' : 'red'">
            {{ currentNotification.is_read ? '已读' : '未读' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="发送时间">
          {{ formatDateTime(currentNotification.created_at) }}
        </a-descriptions-item>
        <a-descriptions-item label="内容" v-if="currentNotification.content">
          <div class="notification-content">{{ currentNotification.content }}</div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import {
  BellOutlined,
  NotificationOutlined,
  PlusCircleOutlined,
  SendOutlined,
  UserOutlined,
  ReloadOutlined,
  EyeOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import {
  getAdminNotifications,
  sendAdminNotification,
  deleteAdminNotification,
  getNotificationStats
} from '@/api/notification'
import { getAllUsers } from '@/api/user'
import dayjs from 'dayjs'

const loading = ref(false)
const sending = ref(false)
const notifications = ref([])
const stats = ref({
  total_count: 0,
  system_count: 0,
  today_count: 0,
  type_stats: {}
})
const userOptions = ref([])

const filters = reactive({
  user_id: undefined,
  notification_type: undefined,
  is_system: undefined
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  showTotal: (total) => `共 ${total} 条`
})

const showSendModal = ref(false)
const showDetailModal = ref(false)
const currentNotification = ref(null)

const sendForm = reactive({
  title: '',
  content: '',
  type: 5,
  target_type: 'all',
  target_user_ids: []
})

const columns = [
  {
    title: 'ID',
    dataIndex: 'id',
    key: 'id',
    width: 80
  },
  {
    title: '标题',
    dataIndex: 'title',
    key: 'title',
    ellipsis: true
  },
  {
    title: '类型',
    dataIndex: 'type',
    key: 'type',
    width: 120
  },
  {
    title: '接收者',
    dataIndex: 'username',
    key: 'username',
    width: 120
  },
  {
    title: '来源',
    dataIndex: 'is_system',
    key: 'is_system',
    width: 100
  },
  {
    title: '状态',
    dataIndex: 'is_read',
    key: 'is_read',
    width: 80
  },
  {
    title: '发送时间',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
    customRender: ({ text }) => formatDateTime(text)
  },
  {
    title: '操作',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

const fetchNotifications = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.current,
      size: pagination.pageSize,
      ...filters
    }
    
    // Remove undefined values
    Object.keys(params).forEach(key => {
      if (params[key] === undefined || params[key] === null) {
        delete params[key]
      }
    })

    const res = await getAdminNotifications(params)
    if (res.data) {
      notifications.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    message.error('获取通知列表失败')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    const res = await getNotificationStats()
    if (res.data) {
      stats.value = res.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchUsers = async () => {
  try {
    const res = await getAllUsers()
    if (res.data) {
      userOptions.value = res.data.map(user => ({
        label: `${user.username} (${user.nickname || '无昵称'})`,
        value: user.id
      }))
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
  }
}

const handleFilterChange = () => {
  pagination.current = 1
  fetchNotifications()
}

const handleReset = () => {
  filters.user_id = undefined
  filters.notification_type = undefined
  filters.is_system = undefined
  pagination.current = 1
  fetchNotifications()
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchNotifications()
}

const handleTargetTypeChange = () => {
  if (sendForm.target_type === 'all') {
    sendForm.target_user_ids = []
  }
}

const handleSendNotification = async () => {
  if (!sendForm.title.trim()) {
    message.warning('请输入通知标题')
    return
  }

  sending.value = true
  try {
    const data = {
      title: sendForm.title,
      content: sendForm.content || null,
      type: sendForm.type,
      target_user_ids: sendForm.target_type === 'specific' && sendForm.target_user_ids.length > 0 
        ? sendForm.target_user_ids 
        : null
    }

    const res = await sendAdminNotification(data)
    if (res.code === 200) {
      message.success(res.message || '发送成功')
      showSendModal.value = false
      handleCancelSend()
      fetchNotifications()
      fetchStats()
    }
  } catch (error) {
    message.error('发送失败')
  } finally {
    sending.value = false
  }
}

const handleCancelSend = () => {
  sendForm.title = ''
  sendForm.content = ''
  sendForm.type = 5
  sendForm.target_type = 'all'
  sendForm.target_user_ids = []
}

const handleViewDetail = (record) => {
  currentNotification.value = record
  showDetailModal.value = true
}

const handleDelete = async (id) => {
  try {
    await deleteAdminNotification(id)
    message.success('删除成功')
    fetchNotifications()
    fetchStats()
  } catch (error) {
    message.error('删除失败')
  }
}

const getTypeName = (type) => {
  const typeMap = {
    1: '文章下架',
    2: '评论审核',
    3: '新评论',
    4: '系统公告',
    5: '管理员通知'
  }
  return typeMap[type] || '未知'
}

const getTypeColor = (type) => {
  const colorMap = {
    1: 'red',
    2: 'orange',
    3: 'green',
    4: 'blue',
    5: 'purple'
  }
  return colorMap[type] || 'default'
}

const formatDateTime = (datetime) => {
  return datetime ? dayjs(datetime).format('YYYY-MM-DD HH:mm:ss') : '-'
}

onMounted(() => {
  fetchNotifications()
  fetchStats()
  fetchUsers()
})
</script>

<style scoped lang="less">
.admin-notification-container {
  padding: 24px;
}

.stat-card {
  border-radius: 8px;
  transition: all 0.3s;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  :deep(.ant-statistic-title) {
    color: var(--text-secondary);
    font-size: 14px;
  }

  :deep(.ant-statistic-content) {
    color: var(--text-primary);
    font-weight: 600;
  }
}

.send-card {
  cursor: pointer;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .send-action {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 60px;
    color: white;
    
    .send-icon {
      font-size: 24px;
      margin-right: 8px;
    }
    
    .send-text {
      font-size: 18px;
      font-weight: 600;
    }
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
}

.table-card {
  border-radius: 8px;

  .card-header {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 4px;
}

.form-tip {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.notification-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
}

:global(body.dark-theme) {
  .stat-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
  }

  .table-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
  }

  .filter-section {
    background: var(--bg-secondary);
  }
}
</style>
