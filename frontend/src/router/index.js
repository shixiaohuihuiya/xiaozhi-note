import { createRouter, createWebHistory } from 'vue-router'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('@/views/Home.vue'),
        meta: { title: '首页' }
      },
      {
        path: 'articles',
        name: 'Articles',
        component: () => import('@/views/Articles.vue'),
        meta: { title: '笔记列表' }
      },
      {
        path: 'article/:slug',
        name: 'ArticleDetail',
        component: () => import('@/views/ArticleDetail.vue'),
        meta: { title: '笔记详情' }
      },
      {
        path: 'categories',
        name: 'Categories',
        component: () => import('@/views/Categories.vue'),
        meta: { title: '分类' }
      },
      {
        path: 'tags',
        name: 'Tags',
        component: () => import('@/views/Tags.vue'),
        meta: { title: '标签' }
      },
      {
        path: 'guestbook',
        name: 'Guestbook',
        component: () => import('@/views/Guestbook.vue'),
        meta: { title: '留言墙' }
      },
      {
        path: 'about',
        name: 'About',
        component: () => import('@/views/About.vue'),
        meta: { title: '关于小智' }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', guest: true }
  },
  {
    path: '/editor',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Editor',
        component: () => import('@/views/Editor.vue'),
        meta: { title: '写笔记', requiresAuth: true }
      },
      {
        path: ':id',
        name: 'EditArticle',
        component: () => import('@/views/Editor.vue'),
        meta: { title: '编辑笔记', requiresAuth: true }
      }
    ]
  },
  {
    path: '/user',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: 'profile',
        name: 'UserProfile',
        component: () => import('@/views/UserProfile.vue'),
        meta: { title: '个人中心', requiresAuth: true }
      },
      {
        path: 'articles',
        name: 'MyArticles',
        component: () => import('@/views/MyArticles.vue'),
        meta: { title: '我的笔记', requiresAuth: true }
      },
      {
        path: 'password',
        name: 'ChangePassword',
        component: () => import('@/views/ChangePassword.vue'),
        meta: { title: '修改密码', requiresAuth: true }
      }
    ]
  },
  {
    path: '/notifications',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'MessageCenter',
        component: () => import('@/views/MessageCenter.vue'),
        meta: { title: '消息中心', requiresAuth: true }
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/layouts/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'articles',
        name: 'AdminArticles',
        component: () => import('@/views/admin/Articles.vue'),
        meta: { title: '笔记管理' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'comments',
        name: 'AdminComments',
        component: () => import('@/views/admin/Comments.vue'),
        meta: { title: '评论管理' }
      },
      {
        path: 'categories',
        name: 'AdminCategories',
        component: () => import('@/views/admin/Categories.vue'),
        meta: { title: '分类管理' }
      },
      {
        path: 'images',
        name: 'AdminImages',
        component: () => import('@/views/admin/Images.vue'),
        meta: { title: '图片管理' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/Settings.vue'),
        meta: { title: '站点设置' }
      },
      {
        path: 'tags',
        name: 'AdminTags',
        component: () => import('@/views/admin/Tags.vue'),
        meta: { title: '标签管理' }
      },
      {
        path: 'ai-config',
        name: 'AdminAiConfig',
        component: () => import('@/views/admin/AiConfig.vue'),
        meta: { title: 'AI配置' }
      },
      {
        path: 'notifications',
        name: 'AdminNotifications',
        component: () => import('@/views/admin/Notifications.vue'),
        meta: { title: '通知管理' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 小智笔记` : '小智笔记'
  
  // 延迟获取 userStore，确保 Pinia 已初始化
  let userStore
  try {
    userStore = useUserStore()
  } catch (e) {
    // Pinia 未初始化，继续访问
    next()
    return
  }
  
  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
    return
  }
  
  // 需要管理员权限
  if (to.meta.requiresAdmin) {
    console.log('Admin check:', { isLoggedIn: userStore.isLoggedIn, isAdmin: userStore.isAdmin, userInfo: userStore.userInfo })
    if (!userStore.isLoggedIn) {
      next('/login')
      return
    }
    if (!userStore.isAdmin) {
      message.error('需要管理员权限')
      next('/')
      return
    }
  }

  // 强制修改密码：已登录且必须修改密码的用户，只允许访问密码修改页
  if (userStore.isLoggedIn && userStore.mustChangePassword && to.path !== '/user/password') {
    message.warning('请先修改密码')
    next('/user/password?force=1')
    return
  }

  // 游客页面（已登录用户不能访问）
  if (to.meta.guest && userStore.isLoggedIn) {
    next('/')
    return
  }

  next()
})

export default router
