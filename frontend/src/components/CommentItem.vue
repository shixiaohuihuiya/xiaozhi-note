<template>
  <div :id="`comment-${comment.id}`" class="comment-item" :class="{ 'is-root': isRoot }">
    <div class="comment-main">
      <a-avatar :src="comment.user?.avatar" />
      <div class="comment-body">
        <div class="comment-header">
          <div class="comment-header-left">
            <span class="comment-author">{{ comment.user?.nickname || comment.user?.username }}</span>
            <span v-if="comment.is_author" class="author-badge">作者</span>
            <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
          </div>
          <a-dropdown :trigger="['click']">
            <a-button type="link" size="small" class="comment-more-btn"><MoreOutlined /></a-button>
            <template #overlay>
              <a-menu>
                <a-menu-item v-if="canDelete" @click="$emit('delete', comment)">
                  <span style="color: #ff4d4f">删除</span>
                </a-menu-item>
                <a-menu-item @click="copyCommentLink(comment)">复制评论链接</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
        <p class="comment-content">{{ comment.content }}</p>
        <div class="comment-actions">
          <a-button type="link" size="small" @click="$emit('reply', comment)">回复</a-button>
          <a-button v-if="showExpandToggle" type="link" size="small" @click="toggleExpand">
            {{ expanded ? '收起回复' : `展开回复 (${flattenedReplies.total})` }}
          </a-button>
        </div>

        <!-- 内联回复输入框 -->
        <div v-if="isReplying" class="inline-reply">
          <a-textarea
            v-model:value="replyContent"
            :placeholder="`回复 ${comment.user?.nickname || comment.user?.username}...`"
            :rows="2"
            auto-focus
          />
          <div class="inline-reply-actions">
            <a-button size="small" @click="cancelInlineReply">取消</a-button>
            <a-button type="primary" size="small" :loading="props.isSubmitting" @click="submitInlineReply">回复</a-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 嵌套回复列表：所有回复统一平铺显示 -->
    <div v-if="isRoot && hasReplies && expanded" class="reply-list">
      <div
        v-for="item in flattenedReplies.all"
        :id="`comment-${item.id}`"
        :key="item.id"
        class="flat-reply"
      >
        <div class="flat-reply-main">
          <a-avatar :src="item.user?.avatar" :size="28" />
          <div class="flat-reply-body">
            <div class="flat-reply-header">
              <span class="flat-reply-author">{{ item.user?.nickname || item.user?.username }}</span>
              <span v-if="item.is_author" class="author-badge">作者</span>
              <span class="flat-reply-arrow">▸</span>
              <span class="flat-reply-label">回复</span>
              <span class="flat-reply-target">{{ item._targetUser?.nickname || item._targetUser?.username }}</span>
            </div>
            <p class="flat-reply-content">{{ item.content }}</p>
            <div class="flat-reply-actions">
              <span class="flat-reply-time">{{ formatDate(item.created_at) }}</span>
              <a-button type="link" size="small" @click="$emit('reply', item)">回复</a-button>
              <a-dropdown :trigger="['click']">
                <a-button type="link" size="small" class="comment-more-btn"><MoreOutlined /></a-button>
                <template #overlay>
                  <a-menu>
                    <a-menu-item v-if="canDeleteFlat(item)" @click="$emit('delete', item)">
                      <span style="color: #ff4d4f">删除</span>
                    </a-menu-item>
                    <a-menu-item @click="copyCommentLink(item)">复制评论链接</a-menu-item>
                  </a-menu>
                </template>
              </a-dropdown>
            </div>

            <!-- 内联回复输入框（平铺回复） -->
            <div v-if="activeReplyId === item.id" class="inline-reply">
              <a-textarea
                v-model:value="replyContent"
                :placeholder="`回复 ${item.user?.nickname || item.user?.username}...`"
                :rows="2"
                auto-focus
              />
              <div class="inline-reply-actions">
                <a-button size="small" @click="cancelInlineReply">取消</a-button>
                <a-button type="primary" size="small" :loading="props.isSubmitting" @click="submitFlatReply(item)">回复</a-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { message } from 'ant-design-vue'
import { MoreOutlined } from '@ant-design/icons-vue'
import { formatDate } from '@/utils/date'

const props = defineProps({
  comment: { type: Object, required: true },
  currentUserId: { type: Number, default: null },
  articleAuthorId: { type: Number, default: null },
  isAdmin: { type: Boolean, default: false },
  isRoot: { type: Boolean, default: false },
  activeReplyId: { type: Number, default: null },
  isSubmitting: { type: Boolean, default: false }
})

const emit = defineEmits(['reply', 'delete', 'cancel-reply', 'submit-reply'])

const replyContent = ref('')
const isReplying = computed(() => props.activeReplyId === props.comment.id)

const canDelete = computed(() => {
  if (!props.currentUserId) return false
  return (
    props.currentUserId === props.comment.user?.id ||
    props.currentUserId === props.articleAuthorId ||
    props.isAdmin
  )
})

const expanded = ref(false)

const flattenedReplies = computed(() => {
  const all = []

  if (!props.isRoot || !props.comment.replies?.length) {
    return { all, total: 0 }
  }

  // 按层级广度优先遍历，确保深层回复始终展示在最下面
  let queue = props.comment.replies.map(r => ({ node: r, targetUser: props.comment.user }))

  while (queue.length > 0) {
    const levelSize = queue.length
    const nextQueue = []

    for (let i = 0; i < levelSize; i++) {
      const { node, targetUser } = queue[i]
      all.push({ ...node, _targetUser: targetUser })
      if (node.replies?.length) {
        for (const child of node.replies) {
          nextQueue.push({ node: child, targetUser: node.user })
        }
      }
    }

    queue = nextQueue
  }

  return { all, total: all.length }
})

const hasReplies = computed(() => flattenedReplies.value.all.length > 0)
const showExpandToggle = computed(() => props.isRoot && hasReplies.value)

const toggleExpand = () => {
  expanded.value = !expanded.value
}

const canDeleteFlat = (item) => {
  if (!props.currentUserId) return false
  return (
    props.currentUserId === item.user?.id ||
    props.currentUserId === props.articleAuthorId ||
    props.isAdmin
  )
}

const cancelInlineReply = () => {
  replyContent.value = ''
  emit('cancel-reply')
}

const submitInlineReply = () => {
  if (!replyContent.value.trim()) return
  emit('submit-reply', {
    parent_id: props.comment.id,
    content: replyContent.value.trim()
  })
  replyContent.value = ''
}

const submitFlatReply = (item) => {
  if (!replyContent.value.trim()) return
  emit('submit-reply', {
    parent_id: item.id,
    content: replyContent.value.trim()
  })
  replyContent.value = ''
}

const copyCommentLink = (comment) => {
  const url = `${window.location.origin}${window.location.pathname}#comment-${comment.id}`
  navigator.clipboard.writeText(url).then(() => {
    message.success('评论链接已复制')
  }).catch(() => {
    message.error('复制失败')
  })
}
</script>

<style scoped lang="less">
.comment-item {
  margin-bottom: 16px;

  &.is-root {
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color);

    &:last-child {
      border-bottom: none;
    }
  }

  .author-badge {
    font-size: 12px;
    padding: 2px 8px;
    background: var(--ant-primary-color);
    color: #fff;
    border-radius: 4px;
  }

  .comment-main {
    display: flex;
    gap: 12px;

    .comment-body {
      flex: 1;

      .comment-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 6px;

        .comment-header-left {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1;
          min-width: 0;

          .comment-author {
            font-weight: 500;
            color: var(--text-primary);
          }

          .comment-time {
            font-size: 12px;
            color: var(--text-tertiary);
          }
        }
      }

      .comment-content {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 6px;
      }

      .comment-actions {
        display: flex;
        gap: 8px;
      }

      .inline-reply {
        margin-top: 12px;
        padding: 12px;
        background: var(--bg-secondary);
        border-radius: 8px;

        .inline-reply-actions {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 8px;
        }
      }
    }
  }

  .reply-list {
    margin-top: 12px;
    margin-left: 44px;
    padding-left: 16px;
    border-left: 2px solid var(--border-color);
  }

  .flat-reply {
    margin-bottom: 14px;

    .flat-reply-main {
      display: flex;
      gap: 10px;

      .flat-reply-body {
        flex: 1;

        .flat-reply-header {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-bottom: 4px;

          .flat-reply-author {
            font-weight: 500;
            color: var(--text-primary);
            font-size: 14px;
          }

          .flat-reply-arrow {
            color: var(--ant-primary-color);
            font-size: 12px;
          }

          .flat-reply-label {
            color: var(--text-secondary);
            font-size: 13px;
          }

          .flat-reply-target {
            color: var(--text-secondary);
            font-size: 14px;
          }
        }

        .flat-reply-content {
          color: var(--text-primary);
          font-size: 14px;
          line-height: 1.6;
          margin-bottom: 4px;
        }

        .flat-reply-actions {
          display: flex;
          align-items: center;
          gap: 8px;

          .flat-reply-time {
            font-size: 12px;
            color: var(--text-tertiary);
          }
        }

        .comment-more-btn {
          opacity: 0;
          transition: opacity 0.2s ease;
        }
      }

      &:hover .comment-more-btn {
        opacity: 1;
      }
    }
  }

  .comment-header {
    .comment-more-btn {
      opacity: 0;
      transition: opacity 0.2s ease;
    }
  }
}

.comment-item:hover .comment-header .comment-more-btn {
  opacity: 1;
}
</style>
