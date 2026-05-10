<template>
  <div class="page-container">
    <div class="content-wrapper">
      <a-card class="message-card" :bordered="false">
        <template #title>
          <div class="card-title">
            <BellOutlined />
            <span>消息中心</span>
            <a-tag v-if="unreadCount > 0" color="red">{{ unreadCount }}条未读</a-tag>
          </div>
        </template>
        <template #extra>
          <a-button
            v-if="notifications.length > 0"
            type="link"
            @click="handleMarkAllRead"
            :loading="markAllLoading"
          >
            <CheckOutlined /> 全部已读
          </a-button>
        </template>

        <a-list
          :loading="loading"
          :data-source="notifications"
          :pagination="pagination"
          class="notification-list"
        >
          <template #renderItem="{ item }">
            <a-list-item
              class="notification-list-item"
              :class="{ unread: !item.is_read }"
            >
              <a-list-item-meta @click="handleItemClick(item)">
                <template #avatar>
                  <a-avatar
                    :style="{
                      backgroundColor: item.type === 1 ? '#ff4d4f' : item.type === 3 ? '#52c41a' : '#faad14'
                    }"
                  >
                    <template #icon>
                      <FileTextOutlined v-if="item.type === 1" />
                      <CommentOutlined v-else-if="item.type === 3" />
                      <CommentOutlined v-else />
                    </template>
                  </a-avatar>
                </template>
                <template #title>
                  <div class="meta-title">
                    <span>{{ item.title }}</span>
                    <a-tag v-if="!item.is_read" color="red">未读</a-tag>
                  </div>
                </template>
                <template #description>
                  <div class="meta-desc">
                    <p v-if="item.content" class="content-text">{{ item.content }}</p>
                    <span class="time-text">{{ formatTime(item.created_at) }}</span>
                  </div>
                </template>
              </a-list-item-meta>
              <template #actions>
                <a-dropdown placement="bottomRight">
                  <a-button type="text" size="small" class="action-btn">
                    <MoreOutlined />
                  </a-button>
                  <template #overlay>
                    <a-menu @click="({ key }) => handleNotifyAction(key, item)">
                      <a-menu-item v-if="item.is_read" key="unread">
                        <EyeInvisibleOutlined /> 标记未读
                      </a-menu-item>
                      <a-menu-item v-else key="read">
                        <EyeOutlined /> 标记已读
                      </a-menu-item>
                      <a-menu-divider />
                      <a-menu-item key="delete" class="menu-danger">
                        <DeleteOutlined /> 删除
                      </a-menu-item>
                    </a-menu>
                  </template>
                </a-dropdown>
              </template>
            </a-list-item>
          </template>

          <template #empty>
            <a-empty description="暂无通知">
              <template #image>
                <InboxOutlined style="font-size: 48px; color: var(--text-tertiary); opacity: 0.5;" />
              </template>
            </a-empty>
          </template>
        </a-list>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import {
  BellOutlined,
  CheckOutlined,
  FileTextOutlined,
  CommentOutlined,
  InboxOutlined,
  MoreOutlined,
  DeleteOutlined,
  EyeOutlined,
  EyeInvisibleOutlined
} from '@ant-design/icons-vue'
import { getNotifications, markAsRead, markAsUnread, markAllAsRead, deleteNotification } from '@/api/notification'
import { formatRelativeTime } from '@/utils/date'

const loading = ref(false)
const markAllLoading = ref(false)
const notifications = ref([])
const unreadCount = ref(0)
const router = useRouter()
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50'],
  showTotal: (total) => `共 ${total} 条`,
  onChange: (page, pageSize) => {
    pagination.value.current = page
    pagination.value.pageSize = pageSize
    fetchData()
  }
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getNotifications({
      page: pagination.value.current,
      size: pagination.value.pageSize
    })
    if (res.data) {
      notifications.value = res.data.items || []
      pagination.value.total = res.data.total || 0
      // 计算未读数
      unreadCount.value = notifications.value.filter(n => !n.is_read).length
    }
  } catch (error) {
    message.error('获取通知失败')
  } finally {
    loading.value = false
  }
}

const handleItemClick = async (item) => {
  if (!item.is_read) {
    try {
      await markAsRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      // ignore
    }
  }
  // 评论通知跳转到笔记并定位到评论
  if (item.type === 3 && item.article_slug) {
    router.push(`/article/${item.article_slug}?comment_id=${item.related_id}#comment-${item.related_id}`)
  }
}

const handleNotifyAction = async (key, item) => {
  if (key === 'read') {
    try {
      await markAsRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      message.success('已标记为已读')
    } catch (e) {
      message.error('操作失败')
    }
    return
  }
  if (key === 'unread') {
    try {
      await markAsUnread(item.id)
      item.is_read = false
      unreadCount.value += 1
      message.success('已标记为未读')
    } catch (e) {
      message.error('操作失败')
    }
    return
  }
  if (key === 'delete') {
    Modal.confirm({
      title: '确认删除该通知？',
      content: '删除后不可恢复。',
      okText: '删除',
      okType: 'danger',
      onOk: async () => {
        try {
          await deleteNotification(item.id)
          notifications.value = notifications.value.filter(n => n.id !== item.id)
          if (!item.is_read) {
            unreadCount.value = Math.max(0, unreadCount.value - 1)
          }
          pagination.value.total = Math.max(0, pagination.value.total - 1)
          message.success('删除成功')
        } catch (e) {
          message.error('删除失败')
        }
      }
    })
  }
}

const handleMarkAllRead = async () => {
  markAllLoading.value = true
  try {
    await markAllAsRead()
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
    message.success('已全部标记为已读')
  } catch (error) {
    message.error('操作失败')
  } finally {
    markAllLoading.value = false
  }
}



const formatTime = (time) => formatRelativeTime(time)

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="less">
.page-container {
  min-height: calc(100vh - 64px - 70px);
  background: var(--bg-primary);
  padding: 24px;
}

.content-wrapper {
  max-width: 900px;
  margin: 0 auto;
}

.message-card {
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;

  :deep(.ant-card-head) {
    border-bottom-color: var(--border-color);
    background: transparent;
  }

  :deep(.ant-card-head-title) {
    color: var(--text-primary);
  }
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;

  .anticon {
    color: var(--ant-primary-color);
  }
}

.notification-list {
  :deep(.ant-list-pagination) {
    margin-top: 24px;
    text-align: right;
  }
}

.notification-list-item {
  cursor: pointer;
  padding: 16px;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border-color);

  &:hover {
    background: var(--bg-secondary);
  }

  &.unread {
    background: rgba(24, 144, 255, 0.04);

    :deep(.ant-list-item-meta-title) {
      font-weight: 600;
    }
  }

  :deep(.ant-list-item-meta) {
    align-items: flex-start;
  }

  :deep(.ant-list-item-meta-title) {
    color: var(--text-primary);
  }

  :deep(.ant-list-item-meta-description) {
    color: var(--text-secondary);
  }
}

.meta-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.meta-desc {
  .content-text {
    margin: 4px 0 0;
    color: var(--text-secondary);
    line-height: 1.6;
  }

  .time-text {
    font-size: 12px;
    color: var(--text-tertiary);
    margin-top: 4px;
    display: inline-block;
  }
}

.action-btn {
  color: var(--text-tertiary);
  background: transparent !important;
  border: none !important;
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

:global(body.dark-theme) {
  .message-card {
    :deep(.ant-pagination-item) {
      background: var(--card-bg);
      border-color: var(--border-color);

      a {
        color: var(--text-secondary);
      }

      &:hover a,
      &.ant-pagination-item-active a {
        color: var(--ant-primary-color);
      }
    }

    :deep(.ant-pagination-prev .ant-pagination-item-link,
          .ant-pagination-next .ant-pagination-item-link) {
      background: var(--card-bg);
      border-color: var(--border-color);
      color: var(--text-secondary);
    }

    :deep(.ant-select-selector) {
      background: var(--card-bg) !important;
      border-color: var(--border-color) !important;
      color: var(--text-primary) !important;
    }
  }
}
</style>
