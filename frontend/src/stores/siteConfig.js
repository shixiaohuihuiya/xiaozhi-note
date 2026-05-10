import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getSiteInfo, getThemeConfig } from '@/api/siteConfig'

export const useSiteConfigStore = defineStore('siteConfig', () => {
  const title = ref(localStorage.getItem('site_title') || '小智笔记')
  const description = ref(localStorage.getItem('site_description') || '智能写作助手，让创作更轻松')
  const logo = ref(localStorage.getItem('site_logo') || '')
  const icp = ref(localStorage.getItem('site_icp') || '')
  const footer = ref(localStorage.getItem('site_footer') || '© 2024 小智笔记 - 智能写作助手')
  const codeCopySuffix = ref(localStorage.getItem('site_code_copy_suffix') || '')
  const uptimeDays = ref(parseInt(localStorage.getItem('site_uptime_days')) || 0)
  const loaded = ref(false)

  const applyDocumentTitle = () => {
    if (title.value) document.title = title.value
  }

  const setAll = (data) => {
    if (data.title !== undefined && data.title !== null) {
      title.value = data.title || '小智笔记'
      localStorage.setItem('site_title', title.value)
    }
    if (data.description !== undefined && data.description !== null) {
      description.value = data.description
      localStorage.setItem('site_description', data.description || '')
    }
    if (data.logo !== undefined && data.logo !== null) {
      logo.value = data.logo
      localStorage.setItem('site_logo', data.logo || '')
    }
    if (data.icp !== undefined && data.icp !== null) {
      icp.value = data.icp
      localStorage.setItem('site_icp', data.icp || '')
    }
    if (data.footer !== undefined && data.footer !== null) {
      footer.value = data.footer
      localStorage.setItem('site_footer', data.footer || '')
    }
    if (data.code_copy_suffix !== undefined && data.code_copy_suffix !== null) {
      codeCopySuffix.value = data.code_copy_suffix
      localStorage.setItem('site_code_copy_suffix', data.code_copy_suffix || '')
    }
    if (data.site_uptime_days !== undefined && data.site_uptime_days !== null) {
      uptimeDays.value = data.site_uptime_days
      localStorage.setItem('site_uptime_days', String(data.site_uptime_days))
    }
    applyDocumentTitle()
  }

  const fetchAll = async () => {
    try {
      const res = await getSiteInfo()
      if (res.code === 200 && res.data) {
        setAll(res.data)
      }
    } catch (e) {
      // ignore
    }
    loaded.value = true
  }

  const fetchTheme = async (themeStore) => {
    try {
      const res = await getThemeConfig()
      if (res.code === 200 && res.data) {
        if (res.data.primary_color) {
          themeStore.setPrimaryColor(res.data.primary_color)
        }
      }
    } catch (e) {
      // ignore
    }
  }

  return {
    title,
    description,
    logo,
    icp,
    footer,
    codeCopySuffix,
    uptimeDays,
    loaded,
    setAll,
    fetchAll,
    fetchTheme,
    applyDocumentTitle
  }
})
