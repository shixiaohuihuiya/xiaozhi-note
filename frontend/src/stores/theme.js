import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 主题状态
  const isDark = ref(localStorage.getItem('theme') === 'dark')
  const primaryColor = ref(localStorage.getItem('primaryColor') || '#1890ff')
  
  // 预设主题色
  const presetColors = [
    { name: '科技蓝', value: '#1890ff' },
    { name: '活力橙', value: '#fa8c16' },
    { name: '清新绿', value: '#52c41a' },
    { name: '优雅紫', value: '#722ed1' },
    { name: '浪漫粉', value: '#eb2f96' },
    { name: '深邃青', value: '#13c2c2' },
    { name: '热烈红', value: '#f5222d' }
  ]
  
  // 切换主题模式
  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    updateBodyClass()
  }
  
  // 设置主题色
  const setPrimaryColor = (color) => {
    primaryColor.value = color
    localStorage.setItem('primaryColor', color)
    updateCssVariables()
  }
  
  // 更新 CSS 变量
  const updateCssVariables = () => {
    const root = document.documentElement
    root.style.setProperty('--ant-primary-color', primaryColor.value)
    root.style.setProperty('--ant-primary-color-hover', adjustColor(primaryColor.value, -20))
  }
  
  // 调整颜色亮度
  const adjustColor = (color, amount) => {
    const usePound = color[0] === '#'
    const col = usePound ? color.slice(1) : color
    const num = parseInt(col, 16)
    let r = (num >> 16) + amount
    let g = ((num >> 8) & 0x00FF) + amount
    let b = (num & 0x0000FF) + amount
    r = r > 255 ? 255 : r < 0 ? 0 : r
    g = g > 255 ? 255 : g < 0 ? 0 : g
    b = b > 255 ? 255 : b < 0 ? 0 : b
    return (usePound ? '#' : '') + (g | (b << 8) | (r << 16)).toString(16).padStart(6, '0')
  }
  
  // 更新body类名
  const updateBodyClass = () => {
    if (isDark.value) {
      document.body.classList.add('dark-theme')
      document.body.classList.remove('light-theme')
    } else {
      document.body.classList.add('light-theme')
      document.body.classList.remove('dark-theme')
    }
  }
  
  // 初始化主题
  const initTheme = () => {
    updateBodyClass()
    updateCssVariables()
  }
  
  return {
    isDark,
    primaryColor,
    presetColors,
    toggleTheme,
    setPrimaryColor,
    initTheme
  }
})
