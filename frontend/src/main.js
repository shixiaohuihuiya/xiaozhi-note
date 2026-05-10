import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'
import router from './router'

// 样式导入顺序很重要
import 'ant-design-vue/dist/reset.css'
import './styles/theme.less'
import './styles/global.less'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia)

// 初始化主题（必须在 Pinia 创建之后，App 挂载之前）
import { useThemeStore } from './stores/theme'
import { useSiteConfigStore } from './stores/siteConfig'
const themeStore = useThemeStore()
themeStore.initTheme()

// 加载站点配置（标题/Logo/页脚）和后端主题色
const siteConfigStore = useSiteConfigStore()
siteConfigStore.applyDocumentTitle()
siteConfigStore.fetchAll()
siteConfigStore.fetchTheme(themeStore)

app.use(router)
app.use(Antd)

app.mount('#app')
