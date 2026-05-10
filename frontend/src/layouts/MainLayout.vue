<template>
  <a-layout class="main-layout">
    <!-- Header -->
    <a-layout-header class="header">
      <div class="header-content">
        <!-- Logo (hidden on mobile) -->
        <div class="logo" @click="$router.push('/')">
          <img
            :src="logoSrc"
            alt="logo"
            @error="handleLogoError"
            v-show="logoLoaded"
          />
          <span v-if="!logoLoaded" class="logo-fallback">
            <EditOutlined />
          </span>
          <span>{{ siteConfig.title }}</span>
        </div>

        <!-- Mobile Menu Button (visible only on mobile) -->
        <a-button
          type="text"
          class="mobile-menu-btn"
          @click="mobileMenuVisible = true"
        >
          <MenuOutlined style="font-size: 20px;" />
        </a-button>

        <!-- Desktop Navigation -->
        <a-menu
          mode="horizontal"
          :selected-keys="[currentRoute]"
          class="desktop-nav"
        >
          <a-menu-item key="Home" @click="$router.push('/')">
            <HomeOutlined /> 首页
          </a-menu-item>
          <a-menu-item key="Articles" @click="$router.push('/articles')">
            <FileTextOutlined /> 笔记
          </a-menu-item>
          <a-menu-item key="Categories" @click="$router.push('/categories')">
            <FolderOutlined /> 分类
          </a-menu-item>
          <a-menu-item key="Tags" @click="$router.push('/tags')">
            <TagsOutlined /> 标签
          </a-menu-item>
          <a-menu-item key="Guestbook" @click="$router.push('/guestbook')">
            <MessageOutlined /> 留言墙
          </a-menu-item>
          <a-menu-item key="About" @click="$router.push('/about')">
            <InfoCircleOutlined /> 关于
          </a-menu-item>
        </a-menu>

        <!-- Header Actions -->
        <div class="header-actions">
          <!-- GitHub Link -->
          <a-button 
            v-if="githubUrl" 
            type="text" 
            class="github-link" 
            :href="githubUrl" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
          </a-button>

          <!-- Gitee Link -->
          <a-button 
            v-if="giteeUrl" 
            type="text" 
            class="gitee-link" 
            :href="giteeUrl" 
            target="_blank" 
            rel="noopener noreferrer"
          >
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.521 15.701c-.232 1.065-1.178 1.874-2.319 1.874H9.28c-1.299 0-2.357-1.058-2.357-2.357V9.28c0-1.299 1.058-2.357 2.357-2.357h5.922c1.299 0 2.357 1.058 2.357 2.357v1.178c0 .65-.529 1.178-1.178 1.178h-3.543c-.65 0-1.178.529-1.178 1.178v1.178c0 .65.529 1.178 1.178 1.178h2.364c.65 0 1.178.529 1.178 1.178v.357z"/>
            </svg>
          </a-button>

          <!-- Theme Color Picker -->
          <a-dropdown placement="bottomRight">
            <a-button type="text">
              <BgColorsOutlined />
            </a-button>
            <template #overlay>
              <a-menu @click="handleThemeColorChange">
                <a-menu-item key="#1890ff">
                  <span class="color-dot" style="background: #1890ff"></span>
                  默认蓝
                </a-menu-item>
                <a-menu-item key="#52c41a">
                  <span class="color-dot" style="background: #52c41a"></span>
                  清新绿
                </a-menu-item>
                <a-menu-item key="#faad14">
                  <span class="color-dot" style="background: #faad14"></span>
                  活力橙
                </a-menu-item>
                <a-menu-item key="#f5222d">
                  <span class="color-dot" style="background: #f5222d"></span>
                  热情红
                </a-menu-item>
                <a-menu-item key="#722ed1">
                  <span class="color-dot" style="background: #722ed1"></span>
                  优雅紫
                </a-menu-item>
                <a-menu-item key="#13c2c2">
                  <span class="color-dot" style="background: #13c2c2"></span>
                  天空蓝
                </a-menu-item>
                <a-menu-item key="#eb2f96">
                  <span class="color-dot" style="background: #eb2f96"></span>
                  樱花粉
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>

          <!-- Dark/Light Mode Toggle -->
          <a-button type="text" @click="themeStore.toggleTheme" :title="themeStore.isDark ? '切换到亮色模式' : '切换到暗色模式'">
            <span v-if="themeStore.isDark">🌙</span>
            <span v-else>☀️</span>
          </a-button>

          <!-- Notifications -->
          <a-dropdown
            v-if="userStore.isLoggedIn"
            placement="bottomRight"
            trigger="click"
            @openChange="handleNotificationOpen"
          >
            <a-badge :count="unreadCount" :offset="[4, 0]">
              <a-button type="text">
                <BellOutlined />
              </a-button>
            </a-badge>
            <template #overlay>
              <a-menu class="notification-dropdown">
                <div class="notification-header">
                  <span>通知</span>
                  <a-button type="link" size="small" @click="markAllRead" v-if="unreadCount > 0">
                    全部已读
                  </a-button>
                </div>
                <a-divider style="margin: 8px 0" />
                <div class="notification-list">
                  <a-menu-item
                    v-for="item in notifications"
                    :key="item.id"
                    @click="handleNotificationClick(item)"
                  >
                    <div class="notification-item" :class="{ 'is-read': item.is_read }">
                      <InboxOutlined class="notification-icon" />
                      <div class="notification-content">
                        <div class="notification-title">{{ item.title }}</div>
                        <div class="notification-time">{{ formatTime(item.created_at) }}</div>
                      </div>
                    </div>
                  </a-menu-item>
                  <a-menu-item v-if="notifications.length === 0" disabled>
                    <div class="empty-notification">暂无通知</div>
                  </a-menu-item>
                </div>
                <a-divider style="margin: 8px 0" />
                <a-menu-item @click="goToMessageCenter">
                  <div class="view-all">查看全部</div>
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>

          <!-- Write Article Button -->
          <a-button
            v-if="userStore.isLoggedIn"
            type="primary"
            class="write-article-btn"
            @click="$router.push('/editor')"
          >
            <EditOutlined /> 写笔记
          </a-button>

          <!-- User Menu -->
          <a-dropdown v-if="userStore.isLoggedIn" placement="bottomRight">
            <a-avatar 
              :src="userStore.userInfo?.avatar" 
              :size="32"
              style="cursor: pointer;"
            >
              <UserOutlined />
            </a-avatar>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="goToMessageCenter">
                  <BellOutlined /> 通知中心
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="$router.push('/user/profile')">
                  <UserOutlined /> 个人中心
                </a-menu-item>
                <a-menu-item @click="$router.push('/user/articles')">
                  <FileTextOutlined /> 我的笔记
                </a-menu-item>
                <a-menu-item @click="$router.push('/user/password')">
                  <SafetyOutlined /> 修改密码
                </a-menu-item>
                <a-menu-item v-if="userStore.userInfo?.is_admin" @click="$router.push('/admin')">
                  <InboxOutlined /> 后台管理
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item @click="handleLogout">
                  <LogoutOutlined /> 退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>

          <!-- Login/Register Buttons -->
          <template v-else>
            <a-button @click="$router.push('/login')">登录</a-button>
            <a-button type="primary" @click="$router.push('/register')">注册</a-button>
          </template>
        </div>
      </div>
    </a-layout-header>

    <!-- Mobile Drawer -->
    <a-drawer
      v-model:visible="mobileMenuVisible"
      placement="left"
      :width="280"
      class="mobile-drawer"
    >
      <template #title>
        <div class="mobile-menu-header">
          <div class="logo">
            <img
              :src="logoSrc"
              alt="logo"
              @error="handleLogoError"
              v-show="logoLoaded"
            />
            <span v-if="!logoLoaded" class="logo-fallback">
              <EditOutlined />
            </span>
            <span>{{ siteConfig.title }}</span>
          </div>
        </div>
      </template>
      <a-menu
        mode="vertical"
        :selected-keys="[currentRoute]"
        class="mobile-nav"
      >
        <a-menu-item key="Home" @click="navigateAndClose('/')">
          <HomeOutlined /> 首页
        </a-menu-item>
        <a-menu-item key="Articles" @click="navigateAndClose('/articles')">
          <FileTextOutlined /> 笔记
        </a-menu-item>
        <a-menu-item key="Categories" @click="navigateAndClose('/categories')">
          <FolderOutlined /> 分类
        </a-menu-item>
        <a-menu-item key="Tags" @click="navigateAndClose('/tags')">
          <TagsOutlined /> 标签
        </a-menu-item>
        <a-menu-item key="Guestbook" @click="navigateAndClose('/guestbook')">
          <MessageOutlined /> 留言墙
        </a-menu-item>
        <a-menu-item key="About" @click="navigateAndClose('/about')">
          <InfoCircleOutlined /> 关于
        </a-menu-item>
      </a-menu>

      <!-- Mobile Drawer Extra Actions -->
      <div class="mobile-drawer-actions">
        <a-divider />
        
        <!-- GitHub & Gitee Links -->
        <div class="mobile-repo-links" v-if="githubUrl || giteeUrl">
          <a-button 
            v-if="githubUrl"
            type="text" 
            class="github-link" 
            :href="githubUrl" 
            target="_blank"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            GitHub
          </a-button>
          <a-button 
            v-if="giteeUrl"
            type="text" 
            class="gitee-link" 
            :href="giteeUrl" 
            target="_blank"
          >
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.521 15.701c-.232 1.065-1.178 1.874-2.319 1.874H9.28c-1.299 0-2.357-1.058-2.357-2.357V9.28c0-1.299 1.058-2.357 2.357-2.357h5.922c1.299 0 2.357 1.058 2.357 2.357v1.178c0 .65-.529 1.178-1.178 1.178h-3.543c-.65 0-1.178.529-1.178 1.178v1.178c0 .65.529 1.178 1.178 1.178h2.364c.65 0 1.178.529 1.178 1.178v.357z"/>
            </svg>
            Gitee
          </a-button>
        </div>

        <!-- Theme Colors -->
        <a-divider />
        <div class="mobile-theme-section">
          <div class="mobile-theme-label">主题颜色</div>
          <div class="mobile-theme-colors">
            <a-button 
              v-for="color in ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96']" 
              :key="color"
              class="mobile-color-dot"
              :style="{ background: color }"
              @click="handleThemeColorChange({ key: color })"
            />
          </div>
        </div>

        <!-- Write Article & User Actions -->
        <a-divider />
        <div class="mobile-user-actions">
          <a-button
            v-if="userStore.isLoggedIn"
            type="primary"
            block
            class="write-article-btn"
            @click="navigateAndClose('/editor')"
          >
            <EditOutlined /> 写笔记
          </a-button>
          <div v-if="userStore.isLoggedIn" class="mobile-user-menu">
            <a-button block @click="navigateAndClose('/user/profile')">
              <UserOutlined /> 个人中心
            </a-button>
            <a-button block @click="navigateAndClose('/user/articles')">
              <FileTextOutlined /> 我的笔记
            </a-button>
            <a-button block @click="navigateAndClose('/user/password')">
              <SafetyOutlined /> 修改密码
            </a-button>
            <a-button block v-if="userStore.userInfo?.is_admin" @click="navigateAndClose('/admin')">
              <InboxOutlined /> 后台管理
            </a-button>
            <a-button block danger @click="handleLogout">
              <LogoutOutlined /> 退出登录
            </a-button>
          </div>
          <div v-else class="mobile-login-buttons">
            <a-button block @click="navigateAndClose('/login')">登录</a-button>
            <a-button block type="primary" @click="navigateAndClose('/register')">注册</a-button>
          </div>
        </div>
      </div>
    </a-drawer>

    <!-- Content -->
    <a-layout-content class="content">
      <router-view />
    </a-layout-content>

    <!-- Footer -->
    <a-layout-footer class="footer">
      <div class="footer-main">
        <!-- Left: Brand Info -->
        <div class="footer-brand">
          <div class="footer-logo">
            <img
              :src="logoSrc"
              alt="logo"
              @error="handleLogoError"
              v-show="logoLoaded"
              class="footer-logo-img"
            />
            <span v-if="!logoLoaded" class="footer-logo-icon">
              <EditOutlined />
            </span>
            <span>{{ siteConfig.title }}</span>
          </div>
          <p class="footer-description">{{ siteConfig.footer || '一个简洁、美观的笔记管理平台' }}</p>
        </div>

        <!-- Center: Links -->
        <div class="footer-links">
          <div class="footer-column">
            <h4>导航</h4>
            <a @click="$router.push('/')">首页</a>
            <a @click="$router.push('/articles')">笔记</a>
            <a @click="$router.push('/categories')">分类</a>
            <a @click="$router.push('/tags')">标签</a>
          </div>
          <div class="footer-column">
            <h4>互动</h4>
            <a @click="$router.push('/guestbook')">留言墙</a>
            <a @click="$router.push('/about')">关于</a>
            <a v-if="userStore.isLoggedIn" @click="$router.push('/editor')">写笔记</a>
          </div>
        </div>

        <!-- Right: Social & Contact -->
        <div class="footer-social">
          <h4>联系我们</h4>
          <div class="social-icons">
            <!-- 抖音 -->
            <div class="social-icon-wrapper">
              <a 
                href="#" 
                target="_blank" 
                rel="noopener noreferrer"
                class="social-icon social-icon-douyin"
                title="抖音"
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                </svg>
              </a>
              <div class="qr-code-popup">
                <img src="/douyin.png" alt="抖音二维码" />
              </div>
            </div>
            <!-- 小红书 -->
            <div class="social-icon-wrapper">
              <a 
                href="#" 
                target="_blank" 
                rel="noopener noreferrer"
                class="social-icon social-icon-xiaohongshu"
                title="小红书"
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6h2v6zm4 0h-2v-6h2v6zm-2-8.5a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3z"/>
                </svg>
              </a>
              <div class="qr-code-popup">
                <img src="/xhs.png" alt="小红书二维码" />
              </div>
            </div>
            <!-- 飞书 -->
            <div class="social-icon-wrapper">
              <a 
                href="#" 
                target="_blank" 
                rel="noopener noreferrer"
                class="social-icon social-icon-feishu"
                title="飞书"
              >
                <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </a>
              <div class="qr-code-popup">
                <img src="/feishu.png" alt="飞书二维码" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom: Copyright -->
      <div class="footer-bottom">
        <span>© {{ new Date().getFullYear() }} {{ siteConfig.title }}. All rights reserved.</span>
        <span v-if="siteConfig.icp" class="divider">·</span>
        <span v-if="siteConfig.icp">{{ siteConfig.icp }}</span>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  HomeOutlined,
  FileTextOutlined,
  FolderOutlined,
  TagsOutlined,
  MessageOutlined,
  InfoCircleOutlined,
  BgColorsOutlined,
  EditOutlined,
  UserOutlined,
  LogoutOutlined,
  MenuOutlined,
  SafetyOutlined,
  BellOutlined,
  InboxOutlined,
  BulbOutlined
} from '@ant-design/icons-vue'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import { useSiteConfigStore } from '@/stores/siteConfig'
import { getNotifications, getUnreadCount, markAsRead, markAllAsRead } from '@/api/notification'
import { formatRelativeTime } from '@/utils/date'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const userStore = useUserStore()
const siteConfig = useSiteConfigStore()

// GitHub and Gitee URLs from environment variables
const githubUrl = import.meta.env.VITE_GITHUB_URL || ''
const giteeUrl = import.meta.env.VITE_GITEE_URL || ''

// Logo loading state
const logoLoaded = ref(true)
const logoSrc = ref(siteConfig.logo || '/logo.svg')
const handleLogoError = () => {
  // 如果当前不是默认 logo，尝试回退到 /logo.svg
  if (logoSrc.value !== '/logo.svg') {
    logoSrc.value = '/logo.svg'
  } else {
    logoLoaded.value = false
  }
}

const currentRoute = computed(() => route.name)
const mobileMenuVisible = ref(false)
const notifications = ref([])
const unreadCount = ref(0)

// 获取通知列表（仅未读）
const fetchNotifications = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await getNotifications({ page: 1, size: 5, is_read: false })
    if (res.data) {
      notifications.value = res.data.items || []
    }
  } catch (error) {
    // ignore
  }
}

// 获取未读数量
const fetchUnreadCount = async () => {
  if (!userStore.isLoggedIn) return
  try {
    const res = await getUnreadCount()
    if (res.data) {
      unreadCount.value = res.data.count || 0
    }
  } catch (error) {
    // ignore
  }
}

// 定时刷新未读数
let unreadTimer = null
const startUnreadTimer = () => {
  if (unreadTimer) clearInterval(unreadTimer)
  unreadTimer = setInterval(fetchUnreadCount, 30000)
}
const stopUnreadTimer = () => {
  if (unreadTimer) {
    clearInterval(unreadTimer)
    unreadTimer = null
  }
}

// 下拉打开时刷新
const handleNotificationOpen = (open) => {
  if (open) {
    fetchNotifications()
  }
}

// 点击通知
const handleNotificationClick = async (item) => {
  if (!item.is_read) {
    try {
      await markAsRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch (error) {
      // ignore
    }
  }
  if (item.type === 3 && item.article_slug) {
    router.push(`/article/${item.article_slug}?comment_id=${item.related_id}#comment-${item.related_id}`)
  } else {
    router.push('/notifications')
  }
}

// 全部已读
const markAllRead = async () => {
  try {
    await markAllAsRead()
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
    message.success('已全部标记为已读')
  } catch (error) {
    message.error('操作失败')
  }
}

// 跳转消息中心
const goToMessageCenter = () => {
  router.push('/notifications')
}

// 格式化时间
const formatTime = (time) => formatRelativeTime(time)

const navigateAndClose = (path) => {
  router.push(path)
  mobileMenuVisible.value = false
}

const handleLogout = () => {
  userStore.logout()
  message.success('已退出登录')
  router.push('/')
}

const handleThemeColorChange = ({ key }) => {
  themeStore.setPrimaryColor(key)
  message.success('主题色已切换')
}

// 登录后启动轮询
if (userStore.isLoggedIn) {
  fetchUnreadCount()
  startUnreadTimer()
}

import { watch } from 'vue'
watch(() => userStore.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn) {
    fetchUnreadCount()
    startUnreadTimer()
  } else {
    stopUnreadTimer()
    unreadCount.value = 0
    notifications.value = []
  }
})
</script>

<style scoped lang="less">
.main-layout {
  min-height: 100vh;
  background: var(--bg-primary);
}

.header {
  background: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  
  .header-content {
    max-width: 100%;
    margin: 0 auto;
    display: flex;
    align-items: center;
    padding: 0 24px;
    height: 64px;
    gap: 0;
  }
  
  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    margin-right: 32px;
    flex-shrink: 0;
    
    img {
      width: 32px;
      height: 32px;
    }
    
    .logo-fallback {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      font-size: 20px;
      color: var(--ant-primary-color);
    }
    
    span {
      font-size: 20px;
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
    }
  }
  
  .nav-menu {
    flex: 1;
    background: transparent;
    border-bottom: none;
  }
  
  .desktop-nav {
    flex: 1;
    background: transparent;
    border-bottom: none;
    
    // Force all menu items to be visible, prevent overflow
    :deep(.ant-menu-overflow) {
      display: flex !important;
      flex-wrap: nowrap !important;
      overflow: visible !important;
    }
    
    :deep(.ant-menu-overflow-item) {
      flex-shrink: 0 !important;
      visibility: visible !important;
    }
    
    :deep(.ant-menu-item) {
      white-space: nowrap;
    }
    
    // Hide the overflow dropdown (the "...")
    :deep(.ant-menu-overflow-rest) {
      display: none !important;
      visibility: hidden !important;
      width: 0 !important;
    }
  }
  
  .mobile-menu-btn {
    display: none;
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
    margin-left: auto;
  }
}

// GitHub and Gitee link styles
.github-link, .gitee-link {
  color: var(--text-secondary);
  transition: all 0.2s;
  padding: 4px;
  
  &:hover {
    transform: translateY(-1px);
  }
}

.github-link {
  &:hover {
    color: #333;
  }
}

.gitee-link {
  &:hover {
    color: #c71d23;
  }
}

.dark-theme {
  .github-link:hover {
    color: #fff;
  }
  
  .gitee-link:hover {
    color: #ff6b6b;
  }
}

.content {
  min-height: calc(100vh - 64px - 70px);
  
  // Notebook grid paper background - covers entire page area
  background-color: #fefefe;
  background-image: 
    linear-gradient(to right, rgba(0, 0, 0, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.03) 1px, transparent 1px);
  background-size: 
    24px 100%,
    100% 32px;
  background-position: 0 0;
  
  // Dark mode
  .dark-theme & {
    background-color: #1a1a1a;
    background-image: 
      linear-gradient(to right, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  }
}

.footer {
  background: var(--bg-secondary);
  border-top: 1px solid var(--border-color);
  padding: 48px 24px 24px;
  
  .footer-main {
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 48px;
    padding-bottom: 32px;
    border-bottom: 1px solid var(--border-color);
    
    .footer-brand {
      .footer-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        
        .footer-logo-icon {
          width: 40px;
          height: 40px;
          background: var(--ant-primary-color);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 20px;
        }
        
        .footer-logo-img {
          width: 40px;
          height: 40px;
          object-fit: contain;
        }
        
        span {
          font-size: 20px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
      
      .footer-description {
        color: var(--text-secondary);
        font-size: 14px;
        line-height: 1.6;
        margin: 0;
        max-width: 320px;
      }
    }
    
    .footer-links {
      display: flex;
      gap: 48px;
      
      .footer-column {
        h4 {
          font-size: 14px;
          font-weight: 600;
          color: var(--text-primary);
          margin: 0 0 16px 0;
        }
        
        a {
          display: block;
          color: var(--text-secondary);
          font-size: 14px;
          text-decoration: none;
          padding: 6px 0;
          transition: color 0.2s;
          cursor: pointer;
          
          &:hover {
            color: var(--ant-primary-color);
          }
        }
      }
    }
    
    .footer-social {
      h4 {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0 0 16px 0;
      }
      
      .social-icons {
        display: flex;
        gap: 16px;
        
        .social-icon-wrapper {
          position: relative;
          display: inline-block;
          
          // Invisible hover area that covers both icon and popup
          &::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: -30px;
            right: -30px;
            height: 200px;
            z-index: 1;
          }
          
          // Make the link also part of the hover area
          .social-icon {
            position: relative;
            z-index: 2;
          }
          
          &:hover .qr-code-popup {
            opacity: 1;
            visibility: visible;
            transform: translateX(-50%) translateY(0);
            z-index: 1000;
          }
        }
        
        .qr-code-popup {
          position: absolute;
          bottom: 46px;
          left: 50%;
          transform: translateX(-50%) translateY(10px);
          background: white;
          border-radius: 8px;
          padding: 12px;
          padding-bottom: 8px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
          opacity: 0;
          visibility: hidden;
          transition: all 0.3s ease;
          z-index: 999;
          
          img {
            width: 150px;
            height: 150px;
            object-fit: contain;
            display: block;
          }
          
          // Arrow pointer
          &::after {
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border-width: 6px;
            border-style: solid;
            border-color: white transparent transparent transparent;
          }
        }
        
        .social-icon {
          width: 36px;
          height: 36px;
          border-radius: 8px;
          background: var(--bg-primary);
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--text-secondary);
          transition: all 0.2s;
          text-decoration: none;
          
          &:hover {
            color: white;
            transform: translateY(-2px);
          }
          
          // 抖音 - 黑红色
          &.social-icon-douyin:hover {
            background: #000000;
          }
          
          // 小红书 - 红色
          &.social-icon-xiaohongshu:hover {
            background: #ff2442;
          }
          
          // 飞书 - 蓝色
          &.social-icon-feishu:hover {
            background: #00d6b9;
          }
        }
      }
    }
  }
  
  .footer-bottom {
    max-width: 1200px;
    margin: 24px auto 0;
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--text-tertiary);
    font-size: 13px;
    
    .divider {
      color: var(--text-tertiary);
    }
  }
}

.color-dot {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}

// 移动端菜单按钮
.mobile-menu-btn {
  display: none;
  font-size: 20px;
  color: var(--text-primary);
}

// 响应式布局
@media (max-width: 768px) {
  .header {
    .header-content {
      padding: 0 8px;
      gap: 8px;
    }
    
    // Hide logo and title on mobile
    .logo {
      display: none;
    }
    
    // Show mobile hamburger menu
    .mobile-menu-btn {
      display: flex !important;
      align-items: center;
      justify-content: center;
      margin-right: 0;
      padding: 4px;
      min-width: 32px;
    }
    
    .desktop-nav {
      display: none !important;
    }
    
    // Align header actions icons evenly
    .header-actions {
      gap: 4px;
      margin-left: auto;
      
      .ant-btn {
        padding: 4px;
        min-width: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }
  }
}

// 移动端抽屉
.mobile-drawer {
  .mobile-menu-header {
    padding: 16px;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 8px;
    
    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
      
      img {
        width: 32px;
        height: 32px;
      }
      
      .logo-fallback {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        font-size: 20px;
        color: var(--ant-primary-color);
      }
      
      span {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }
  }
  
  .mobile-nav {
    border-right: none;
    background: transparent;
    
    .ant-menu-item {
      color: var(--text-secondary);
      
      &:hover {
        color: var(--text-primary);
      }
      
      &.ant-menu-item-selected {
        color: var(--ant-primary-color);
        background: rgba(24, 144, 255, 0.1);
      }
    }
  }

  // Mobile drawer extra actions section
  .mobile-drawer-actions {
    padding: 16px;
    
    .mobile-repo-links {
      display: flex;
      gap: 12px;
      justify-content: center;
      
      .ant-btn {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }
    }

    .mobile-theme-section {
      .mobile-theme-label {
        font-size: 13px;
        color: var(--text-secondary);
        margin-bottom: 12px;
        text-align: center;
      }
      
      .mobile-theme-colors {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        
        .mobile-color-dot {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          border: 2px solid transparent;
          padding: 0;
          transition: all 0.2s;
          
          &:hover {
            transform: scale(1.1);
          }
          
          &::after {
            display: none;
          }
        }
      }
    }

    .mobile-user-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
      
      .mobile-user-menu,
      .mobile-login-buttons {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }
      
      .ant-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }
    }
  }
}

// 暗色模式下的水平导航菜单
.dark-theme {
  .nav-menu {
    &.ant-menu-horizontal {
      background: transparent;
      
      .ant-menu-item {
        color: var(--text-secondary);
        border-radius: 6px;
        margin: 0 4px;
        transition: all 0.2s;
        
        &:hover {
          color: var(--text-primary);
          background: rgba(255, 255, 255, 0.08);
        }
        
        &.ant-menu-item-selected {
          color: var(--ant-primary-color);
          background: rgba(255, 255, 255, 0.06);
        }
        
        &::after {
          border-bottom-color: var(--ant-primary-color);
        }
      }
    }
  }
  
  // 下拉菜单
  .ant-dropdown-menu {
    background: var(--card-bg) !important;
    
    .ant-dropdown-menu-item {
      color: var(--text-primary) !important;
      
      &:hover {
        background: var(--bg-tertiary) !important;
      }
      
      .ant-dropdown-menu-title-content {
        color: var(--text-primary) !important;
      }
      
      span {
        color: var(--text-primary) !important;
      }
    }
  }
  
  // 头部按钮图标
  .header-actions {
    .ant-btn {
      color: var(--text-secondary);
      
      &:hover {
        color: var(--text-primary);
        background: var(--bg-tertiary);
      }
      
      .anticon {
        color: var(--text-secondary);
      }
    }
    
    // 写笔记按钮在暗色模式下更醒目
    .write-article-btn {
      background: #1890ff;
      border-color: #1890ff;
      color: #fff;
      font-weight: 500;
      box-shadow: 0 0 8px rgba(24, 144, 255, 0.4);
      
      &:hover {
        background: #40a9ff;
        border-color: #40a9ff;
        color: #fff;
        box-shadow: 0 0 12px rgba(24, 144, 255, 0.6);
      }
      
      .anticon {
        color: #fff;
      }
    }
  }
}

// Notification Dropdown Styles
.notification-dropdown {
  width: 320px;
  
  .notification-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 16px;
    font-weight: 500;
  }
  
  .notification-list {
    max-height: 300px;
    overflow-y: auto;
    
    .notification-item {
      display: flex;
      gap: 12px;
      padding: 8px 0;
      
      &.is-read {
        opacity: 0.6;
      }
      
      .notification-icon {
        font-size: 20px;
        color: var(--ant-primary-color);
        margin-top: 2px;
      }
      
      .notification-content {
        flex: 1;
        
        .notification-title {
          font-size: 14px;
          color: var(--text-primary);
          margin-bottom: 4px;
        }
        
        .notification-time {
          font-size: 12px;
          color: var(--text-tertiary);
        }
      }
    }
    
    .empty-notification {
      text-align: center;
      padding: 20px 0;
      color: var(--text-tertiary);
    }
  }
  
  .view-all {
    text-align: center;
    color: var(--ant-primary-color);
    font-weight: 500;
  }
}

// Footer mobile responsive
@media (max-width: 768px) {
  .footer {
    padding: 32px 16px 16px;
    
    .footer-main {
      grid-template-columns: 1fr;
      gap: 32px;
      padding-bottom: 24px;
      
      .footer-brand {
        text-align: center;
        
        .footer-logo {
          justify-content: center;
        }
        
        .footer-description {
          max-width: 100%;
          margin: 0 auto;
        }
      }
      
      .footer-links {
        justify-content: center;
        gap: 32px;
        
        .footer-column {
          text-align: center;
        }
      }
      
      .footer-social {
        text-align: center;
        
        .social-icons {
          justify-content: center;
          
          .qr-code-popup {
            img {
              width: 120px;
              height: 120px;
            }
          }
        }
      }
    }
    
    .footer-bottom {
      flex-direction: column;
      text-align: center;
      gap: 4px;
      
      .divider {
        display: none;
      }
    }
  }
}
</style>
