<template>
  <div class="guestbook-danmu">
    <!-- 背景层 -->
    <div class="danmu-bg">
      <div class="bg-grid"></div>
    </div>

    <!-- 标题区 -->
    <div class="danmu-header">
      <h1>留言墙</h1>
      <p>留下你的想法，让文字飘起来</p>
      <div class="online-count" v-if="messages.length">
        <FireOutlined /> {{ messages.length }} 条留言
      </div>
    </div>

    <!-- 飘屏区域 -->
    <div class="danmu-stage" ref="stageRef">
      <TransitionGroup name="danmu">
        <div
          v-for="item in danmuItems"
          :key="item.id"
          class="danmu-item"
          :style="item.style"
          @mouseenter="pauseItem(item)"
          @mouseleave="resumeItem(item)"
          @click="handleDanmuClick(item)"
        >
          <div class="danmu-content" :class="{ 'is-paused': item.paused }">
            <a-avatar :src="item.user?.avatar" :size="24" class="danmu-avatar">
              {{ item.nickname?.[0] || '访' }}
            </a-avatar>
            <span class="danmu-nickname">{{ item.nickname }}</span>
            <span class="danmu-text">{{ item.content }}</span>
            <span class="danmu-like" @click.stop="likeMessage(item)">
              <LikeFilled v-if="item.is_liked" />
              <LikeOutlined v-else />
              {{ item.like_count > 0 ? item.like_count : '' }}
            </span>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <!-- 底部输入区 -->
    <div class="danmu-input-bar">
      <div class="input-wrapper">
        <a-input
          v-model:value="inputContent"
          :maxlength="100"
          placeholder="写下你想说的话，按回车发送..."
          class="danmu-input"
          @pressEnter="submitMessage"
        >
          <template #suffix>
            <span class="input-count">{{ inputContent.length }}/100</span>
          </template>
        </a-input>
        <a-button
          type="primary"
          shape="circle"
          class="send-btn"
          :loading="submitting"
          @click="submitMessage"
        >
          <SendOutlined />
        </a-button>
      </div>
      <div class="input-meta">
        <span v-if="!isLoggedIn">
          <a-input
            v-model:value="form.nickname"
            placeholder="昵称"
            size="small"
            class="meta-input"
          />
        </span>
        <span class="tip">点击飘屏可点赞</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { LikeOutlined, LikeFilled, SendOutlined, FireOutlined } from '@ant-design/icons-vue'
import { getGuestbooks, createGuestbook, likeGuestbook } from '@/api/guestbook'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

const messages = ref([])
const danmuItems = ref([])
const loading = ref(false)
const submitting = ref(false)
const inputContent = ref('')
const stageRef = ref(null)

const form = reactive({
  nickname: '',
  email: '',
  website: ''
})

// 颜色池
const colorPool = [
  '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7',
  '#dfe6e9', '#fd79a8', '#a29bfe', '#00b894', '#e17055',
  '#74b9ff', '#55efc4', '#ff7675', '#fab1a0', '#81ecec'
]

const randomColor = () => colorPool[Math.floor(Math.random() * colorPool.length)]

// 生成随机样式——在整个航道区内随机垂直分布，避免拥挤
const LANES = 10 // 将区域分为10行
const usedLaneCount = ref({}) // 统计每行使用次数用于均匀分布

const pickLane = () => {
  // 优先选择使用次数最少的行
  let minLane = 0
  let minCount = Infinity
  for (let i = 0; i < LANES; i++) {
    const c = usedLaneCount.value[i] || 0
    if (c < minCount) {
      minCount = c
      minLane = i
    }
  }
  usedLaneCount.value[minLane] = (usedLaneCount.value[minLane] || 0) + 1
  return minLane
}

const generateStyle = (index) => {
  const lane = pickLane()
  // 每行占 9%，在其中随机偏移，让垂直位置更分散
  const top = 5 + lane * 9 + Math.random() * 4 // 5%-95%
  const duration = 14 + Math.random() * 12 // 14-26秒，更稳
  const delay = index * 1.2 + Math.random() * 4
  const scale = 0.85 + Math.random() * 0.3
  return {
    top: `${top}%`,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`,
    transform: `scale(${scale})`,
    '--danmu-color': randomColor()
  }
}

const fetchMessages = async () => {
  loading.value = true
  try {
    const res = await getGuestbooks({ page: 1, size: 100 })
    if (res.code === 200) {
      const items = res.data.items || []
      messages.value = items
      // 转换为飘屏数据
      danmuItems.value = items.map((item, index) => ({
        ...item,
        paused: false,
        style: generateStyle(index)
      }))
    }
  } catch (error) {
    message.error('获取留言失败')
  } finally {
    loading.value = false
  }
}

const submitMessage = async () => {
  const content = inputContent.value.trim()
  if (!content) {
    message.warning('请输入留言内容')
    return
  }
  if (content.length > 100) {
    message.warning('留言内容不能超过100字')
    return
  }

  submitting.value = true
  try {
    const data = {
      content,
      nickname: isLoggedIn.value
        ? (userStore.userInfo.nickname || userStore.userInfo.username)
        : (form.nickname || '匿名访客'),
      email: form.email || undefined,
      website: form.website || undefined
    }
    const res = await createGuestbook(data)
    if (res.code === 200) {
      message.success('留言成功')
      inputContent.value = ''
      // 立即添加到飘屏
      const newItem = {
        ...res.data,
        paused: false,
        style: generateStyle(0)
      }
      danmuItems.value.unshift(newItem)
      messages.value.unshift(res.data)
    }
  } catch (error) {
    const msg = error?.response?.data?.detail || error?.response?.data?.message || error?.message || '留言失败'
    message.error(msg)
  } finally {
    submitting.value = false
  }
}

const likeMessage = async (item) => {
  try {
    const res = await likeGuestbook(item.id)
    if (res.code === 200) {
      item.like_count = res.data.like_count
      item.is_liked = true
      message.success('点赞成功')
    }
  } catch (error) {
    message.error('点赞失败')
  }
}

const pauseItem = (item) => {
  item.paused = true
}

const resumeItem = (item) => {
  item.paused = false
}

const handleDanmuClick = (item) => {
  likeMessage(item)
}

onMounted(() => {
  if (isLoggedIn.value && userStore.userInfo) {
    form.nickname = userStore.userInfo.nickname || userStore.userInfo.username
    form.email = userStore.userInfo.email
  }
  fetchMessages()
})
</script>

<style scoped lang="less">
.guestbook-danmu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  background: var(--bg-primary);
  z-index: 1;
}

.danmu-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;

  .bg-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(128, 128, 128, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(128, 128, 128, 0.05) 1px, transparent 1px);
    background-size: 40px 40px;
  }
}

.danmu-header {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 32px 24px 16px;

  h1 {
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 8px;
    background: linear-gradient(135deg, var(--ant-primary-color), #722ed1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  p {
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 8px;
  }

  .online-count {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: var(--text-tertiary);
    padding: 4px 12px;
    background: var(--bg-secondary);
    border-radius: 12px;

    :deep(.anticon) {
      color: #ff4d4f;
    }
  }
}

.danmu-stage {
  position: absolute;
  top: 170px;
  left: 0;
  right: 0;
  bottom: 140px;
  overflow: hidden;
  z-index: 5;
}

.danmu-item {
  position: absolute;
  left: 100%;
  white-space: nowrap;
  animation: danmuMove linear infinite;
  cursor: pointer;
  z-index: 5;

  &:hover {
    z-index: 100;
  }
}

.danmu-content {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: var(--card-bg);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    border-color: var(--danmu-color, var(--ant-primary-color));
  }

  &.is-paused {
    animation-play-state: paused;
  }
}

.danmu-avatar {
  flex-shrink: 0;
}

.danmu-nickname {
  font-weight: 600;
  font-size: 13px;
  color: var(--text-primary);
}

.danmu-text {
  font-size: 14px;
  color: var(--text-secondary);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.danmu-like {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  color: var(--text-tertiary);
  padding: 2px 8px;
  background: var(--bg-secondary);
  border-radius: 10px;
  transition: all 0.2s;

  &:hover {
    color: #ff4d4f;
    background: rgba(255, 77, 79, 0.1);
  }

  :deep(.anticon) {
    font-size: 12px;
  }
}

@keyframes danmuMove {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(calc(-100vw - 100%));
  }
}

/* 进入动画 */
.danmu-enter-active,
.danmu-leave-active {
  transition: opacity 0.5s ease;
}

.danmu-enter-from,
.danmu-leave-to {
  opacity: 0;
}

.danmu-input-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
  padding: 16px 24px;
  backdrop-filter: blur(10px);

  .input-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    max-width: 600px;
    margin: 0 auto;
  }

  .danmu-input {
    flex: 1;

    :deep(.ant-input) {
      border-radius: 24px;
      padding: 8px 16px;
      background: var(--bg-secondary);
      border-color: var(--border-color);
      color: var(--text-primary);

      &::placeholder {
        color: var(--text-tertiary);
      }
    }
  }

  .input-count {
    font-size: 12px;
    color: var(--text-tertiary);
    user-select: none;
  }

  .send-btn {
    width: 44px;
    height: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    :deep(.anticon) {
      font-size: 18px;
    }
  }

  .input-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 600px;
    margin: 8px auto 0;

    .meta-input {
      width: 120px;

      :deep(.ant-input) {
        background: var(--bg-secondary);
        border-color: var(--border-color);
        color: var(--text-primary);
      }
    }

    .tip {
      font-size: 12px;
      color: var(--text-tertiary);
    }
  }
}

@media (max-width: 768px) {
  .danmu-header {
    padding: 20px 16px 12px;

    h1 {
      font-size: 24px;
    }
  }

  .danmu-input-bar {
    padding: 12px 16px;
  }

  .danmu-text {
    max-width: 180px;
  }
}
</style>
