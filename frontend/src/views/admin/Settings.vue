<template>
  <div class="settings-page">
    <h1>站点设置</h1>
    
    <a-tabs v-model:activeKey="activeKey">
      <!-- 主题设置 -->
      <a-tab-pane key="theme" tab="主题设置">
        <a-card title="主题配置" class="settings-card">
          <a-form :model="themeForm" layout="vertical" @finish="saveTheme">
            <a-form-item label="主题色">
              <div class="color-picker">
                <div
                  v-for="color in presetColors"
                  :key="color"
                  class="color-item"
                  :class="{ active: themeForm.primary_color === color }"
                  :style="{ backgroundColor: color }"
                  @click="themeForm.primary_color = color"
                />
              </div>
              <a-input
                v-model:value="themeForm.primary_color"
                placeholder="#1890ff"
                style="margin-top: 12px; width: 200px"
              />
            </a-form-item>
            
            <a-form-item label="默认暗色模式">
              <a-switch v-model:checked="themeForm.dark_mode" />
              <span class="form-hint">开启后站点默认使用暗色主题</span>
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="saving">
                保存主题设置
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
      
      <!-- 站点信息 -->
      <a-tab-pane key="site" tab="站点信息">
        <a-card title="基本信息" class="settings-card">
          <a-form :model="siteForm" layout="vertical" @finish="saveSiteInfo">
            <a-form-item label="站点标题" name="title">
              <a-input v-model:value="siteForm.title" placeholder="小智笔记" />
            </a-form-item>
            
            <a-form-item label="站点描述" name="description">
              <a-textarea
                v-model:value="siteForm.description"
                :rows="3"
                placeholder="智能写作助手，让创作更轻松"
              />
            </a-form-item>
            
            <a-form-item label="站点Logo" name="logo">
              <a-input v-model:value="siteForm.logo" placeholder="Logo URL" />
            </a-form-item>
            
            <a-form-item label="ICP备案号" name="icp">
              <a-input v-model:value="siteForm.icp" placeholder="京ICP备XXXXXXXX号" />
            </a-form-item>
            
            <a-form-item label="页脚信息" name="footer">
              <a-textarea
                v-model:value="siteForm.footer"
                :rows="2"
                placeholder="页脚版权信息"
              />
            </a-form-item>
            
            <a-form-item label="代码复制后缀" name="code_copy_suffix">
              <a-textarea
                v-model:value="siteForm.code_copy_suffix"
                :rows="2"
                placeholder="用户自定义尾缀，会放在标准出处之前"
              />
            </a-form-item>
            
            <a-form-item>
              <a-button type="primary" html-type="submit" :loading="saving">
                保存站点信息
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getThemeConfig, updateThemeConfig, getSiteInfo, updateSiteInfo } from '@/api/siteConfig'
import { useThemeStore } from '@/stores/theme'
import { useSiteConfigStore } from '@/stores/siteConfig'

const themeStore = useThemeStore()
const siteConfigStore = useSiteConfigStore()

const activeKey = ref('theme')
const saving = ref(false)

const presetColors = [
  '#1890ff', // 蓝色
  '#52c41a', // 绿色
  '#faad14', // 黄色
  '#f5222d', // 红色
  '#722ed1', // 紫色
  '#13c2c2', // 青色
  '#eb2f96'  // 粉色
]

const themeForm = reactive({
  primary_color: '#1890ff',
  dark_mode: false
})

const siteForm = reactive({
  title: '',
  description: '',
  logo: '',
  icp: '',
  footer: '',
  code_copy_suffix: ''
})

const fetchThemeConfig = async () => {
  try {
    const res = await getThemeConfig()
    if (res.code === 200) {
      themeForm.primary_color = res.data.primary_color
      themeForm.dark_mode = res.data.dark_mode
    }
  } catch (error) {
    console.error('获取主题配置失败', error)
  }
}

const fetchSiteInfo = async () => {
  try {
    const res = await getSiteInfo()
    if (res.code === 200) {
      Object.assign(siteForm, res.data)
    }
  } catch (error) {
    console.error('获取站点信息失败', error)
  }
}

const saveTheme = async () => {
  if (!themeForm.primary_color) {
    message.error('请选择或输入主题色')
    return
  }
  saving.value = true
  try {
    const res = await updateThemeConfig(themeForm)
    if (res.code === 200) {
      // 立即应用到当前页面
      themeStore.setPrimaryColor(themeForm.primary_color)
      if (themeForm.dark_mode !== themeStore.isDark) {
        themeStore.toggleTheme()
      }
      message.success('主题设置已保存并生效')
    }
  } catch (error) {
    const msg = error?.response?.data?.detail || error?.message || '保存失败'
    message.error(msg)
  } finally {
    saving.value = false
  }
}

const saveSiteInfo = async () => {
  saving.value = true
  try {
    const res = await updateSiteInfo(siteForm)
    if (res.code === 200) {
      // 立即应用到当前页面
      siteConfigStore.setAll(siteForm)
      message.success('站点信息已保存并生效')
    }
  } catch (error) {
    const msg = error?.response?.data?.detail || error?.message || '保存失败'
    message.error(msg)
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchThemeConfig()
  fetchSiteInfo()
})
</script>

<style scoped lang="less">
.settings-page {
  h1 {
    margin-bottom: 24px;
    font-weight: 600;
  }
}

.settings-card {
}

.color-picker {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;

  .color-item {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    border: 2px solid transparent;

    &:hover {
      transform: scale(1.1);
    }

    &.active {
      border-color: var(--text-primary);
      box-shadow: 0 0 0 2px var(--bg-primary), 0 0 0 4px var(--text-primary);
    }
  }
}

.form-hint {
  margin-left: 8px;
  color: var(--text-tertiary);
  font-size: 13px;
}
</style>
