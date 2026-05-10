<template>
  <a-layout class="admin-layout">
    <!-- Mobile Menu Button -->
    <div class="mobile-menu-trigger" v-if="isMobile">
      <a-button type="text" @click="mobileMenuVisible = true">
        <MenuOutlined style="font-size: 20px;" />
      </a-button>
    </div>

    <!-- Desktop Sider -->
    <a-layout-sider
      v-if="!isMobile"
      v-model:collapsed="collapsed"
      collapsible
      :breakpoint="'lg'"
      :collapsed-width="80"
      @breakpoint="onBreakpoint"
    >
      <div class="logo">
        <img v-if="siteConfigStore.logo" :src="logoSrc" @error="handleLogoError" alt="logo" v-show="logoLoaded" class="logo-img" :class="{ 'logo-img-collapsed': collapsed }" />
        <span v-else-if="!collapsed">小智笔记后台</span>
        <span v-else>智</span>
      </div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="handleMenuClick"
      >
        <a-menu-item key="dashboard">
          <DashboardOutlined />
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="articles">
          <FileTextOutlined />
          <span>笔记管理</span>
        </a-menu-item>
        <a-menu-item key="users">
          <UserOutlined />
          <span>用户管理</span>
        </a-menu-item>
        <a-menu-item key="comments">
          <CommentOutlined />
          <span>评论管理</span>
        </a-menu-item>
        <a-menu-item key="categories">
          <FolderOutlined />
          <span>分类管理</span>
        </a-menu-item>
        <a-menu-item key="tags">
          <TagOutlined />
          <span>标签管理</span>
        </a-menu-item>
        <a-menu-item key="images">
          <PictureOutlined />
          <span>图片管理</span>
        </a-menu-item>
        <a-menu-item key="ai-config">
          <RobotOutlined />
          <span>AI配置</span>
        </a-menu-item>
        <a-menu-item key="notifications">
          <BellOutlined />
          <span>通知管理</span>
        </a-menu-item>
        <a-menu-item key="settings">
          <SettingOutlined />
          <span>站点设置</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    
    <a-layout>
      <a-layout-header class="admin-header">
        <div class="header-left">
          <a-breadcrumb>
            <a-breadcrumb-item>
              <router-link to="/admin">首页</router-link>
            </a-breadcrumb-item>
            <a-breadcrumb-item v-if="currentBreadcrumb">
              {{ currentBreadcrumb }}
            </a-breadcrumb-item>
          </a-breadcrumb>
        </div>
        <div class="header-right">
          <a-button type="link" @click="$router.push('/')">返回前台</a-button>
          <a-dropdown>
            <a-avatar :style="{ backgroundColor: themeStore.primaryColor }">
              {{ userStore.userInfo?.nickname?.[0] || 'A' }}
            </a-avatar>
            <template #overlay>
              <a-menu>
                <a-menu-item @click="userStore.logout(); $router.push('/login')">
                  退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>

      <a-layout-content class="admin-content">
        <router-view />
      </a-layout-content>
    </a-layout>

    <!-- Mobile Drawer -->
    <a-drawer
      v-model:visible="mobileMenuVisible"
      placement="left"
      :width="280"
      class="mobile-drawer"
    >
      <template #title>
        <div class="mobile-menu-header">
          <span>后台管理</span>
        </div>
      </template>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="inline"
        @click="handleMobileMenuClick"
      >
        <a-menu-item key="dashboard">
          <DashboardOutlined />
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item key="articles">
          <FileTextOutlined />
          <span>笔记管理</span>
        </a-menu-item>
        <a-menu-item key="users">
          <UserOutlined />
          <span>用户管理</span>
        </a-menu-item>
        <a-menu-item key="comments">
          <CommentOutlined />
          <span>评论管理</span>
        </a-menu-item>
        <a-menu-item key="categories">
          <FolderOutlined />
          <span>分类管理</span>
        </a-menu-item>
        <a-menu-item key="tags">
          <TagOutlined />
          <span>标签管理</span>
        </a-menu-item>
        <a-menu-item key="images">
          <PictureOutlined />
          <span>图片管理</span>
        </a-menu-item>
        <a-menu-item key="ai-config">
          <RobotOutlined />
          <span>AI配置</span>
        </a-menu-item>
        <a-menu-item key="notifications">
          <BellOutlined />
          <span>通知管理</span>
        </a-menu-item>
        <a-menu-item key="settings">
          <SettingOutlined />
          <span>站点设置</span>
        </a-menu-item>
      </a-menu>
      <div class="mobile-drawer-footer">
        <a-button block @click="$router.push('/')">返回前台</a-button>
        <a-button block danger @click="handleLogout">退出登录</a-button>
      </div>
    </a-drawer>
  </a-layout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DashboardOutlined,
  FileTextOutlined,
  UserOutlined,
  CommentOutlined,
  FolderOutlined,
  PictureOutlined,
  SettingOutlined,
  TagOutlined,
  RobotOutlined,
  BellOutlined,
  MenuOutlined
} from '@ant-design/icons-vue'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import { useSiteConfigStore } from '@/stores/siteConfig'

const route = useRoute()
const router = useRouter()
const themeStore = useThemeStore()
const userStore = useUserStore()
const siteConfigStore = useSiteConfigStore()
const logoLoaded = ref(true)
const logoSrc = ref(siteConfigStore.logo || '/logo.svg')
const handleLogoError = () => {
  // 如果当前不是默认 logo，尝试回退到 /logo.svg
  if (logoSrc.value !== '/logo.svg') {
    logoSrc.value = '/logo.svg'
  } else {
    logoLoaded.value = false
  }
}


const collapsed = ref(false)

// Mobile state
const isMobile = ref(window.innerWidth <= 768)
const mobileMenuVisible = ref(false)

const handleResize = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  siteConfigStore.fetchAll()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const breadcrumbMap = {
  'dashboard': '仪表盘',
  'articles': '笔记管理',
  'users': '用户管理',
  'comments': '评论管理',
  'categories': '分类管理',
  'tags': '标签管理',
  'images': '图片管理',
  'ai-config': 'AI配置',
  'notifications': '通知管理',
  'settings': '站点设置'
}

const selectedKeys = computed(() => {
  const path = route.path
  if (path.includes('/admin/articles')) return ['articles']
  if (path.includes('/admin/users')) return ['users']
  if (path.includes('/admin/comments')) return ['comments']
  if (path.includes('/admin/categories')) return ['categories']
  if (path.includes('/admin/tags')) return ['tags']
  if (path.includes('/admin/images')) return ['images']
  if (path.includes('/admin/ai-config')) return ['ai-config']
  if (path.includes('/admin/notifications')) return ['notifications']
  if (path.includes('/admin/settings')) return ['settings']
  return ['dashboard']
})

const currentBreadcrumb = computed(() => {
  const key = selectedKeys.value[0]
  return breadcrumbMap[key] || ''
})

const handleMenuClick = ({ key }) => {
  router.push(`/admin${key === 'dashboard' ? '' : '/' + key}`)
}

const handleMobileMenuClick = ({ key }) => {
  mobileMenuVisible.value = false
  router.push(`/admin${key === 'dashboard' ? '' : '/' + key}`)
}

const onBreakpoint = (broken) => {
  collapsed.value = broken
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped lang="less">
.admin-layout {
  height: 100vh;
  overflow: hidden;

  :deep(.ant-layout-sider) {
    height: 100vh;
    overflow-y: auto;
  }

  > .ant-layout {
    overflow: hidden;
  }
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);

  .logo-img {
    max-height: 36px;
    max-width: 140px;
    object-fit: contain;
    transition: all 0.2s;

    &.logo-img-collapsed {
      max-width: 40px;
      max-height: 28px;
    }
  }
}

.admin-header {
  background: var(--bg-primary);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);

  .header-left {
    display: flex;
    align-items: center;
  }

  :deep(.ant-breadcrumb) {
    color: var(--text-primary);
    a, span {
      color: var(--text-secondary);
    }
    a:hover {
      color: var(--ant-primary-color);
    }
    .ant-breadcrumb-separator {
      color: var(--text-tertiary);
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.admin-content {
  margin: 24px;
  padding: 24px;
  background: var(--bg-primary);
  border-radius: 8px;
  overflow: auto;
  flex: 1;
}

@media (max-width: 768px) {
  .admin-content {
    margin: 8px;
    padding: 12px;
    border-radius: 4px;
  }
  
  .admin-header {
    padding: 0 12px;
    
    .header-left {
      :deep(.ant-breadcrumb) {
        font-size: 12px;
      }
    }
    
    .header-right {
      gap: 8px;
      
      .ant-btn {
        font-size: 12px;
        padding: 0 4px;
      }
      
      .ant-avatar {
        width: 28px !important;
        height: 28px !important;
        font-size: 14px;
      }
    }
  }
  
  // Mobile menu trigger positioned in header
  .mobile-menu-trigger {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 101;
    background: var(--bg-primary);
    padding: 8px 12px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
  }
  
  .admin-header {
    padding-left: 52px; // Make room for hamburger menu
  }
  
  // Mobile drawer styles
  :deep(.mobile-drawer) {
    .ant-drawer-body {
      padding: 0;
      display: flex;
      flex-direction: column;
      
      .mobile-menu-header {
        padding: 16px;
        border-bottom: 1px solid var(--border-color);
        
        span {
          font-size: 18px;
          font-weight: 600;
          color: var(--text-primary);
        }
      }
      
      .ant-menu {
        flex: 1;
        overflow-y: auto;
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
      
      .mobile-drawer-footer {
        padding: 16px;
        border-top: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        gap: 8px;
        
        .ant-btn {
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }
}
</style>
