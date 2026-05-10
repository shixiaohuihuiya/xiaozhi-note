<template>
  <a-config-provider :theme="themeConfig">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { computed, ref } from 'vue'
import { theme } from 'ant-design-vue'

// 安全地获取主题配置
const getThemeStore = () => {
  try {
    const { useThemeStore } = require('@/stores/theme')
    return useThemeStore()
  } catch (e) {
    return null
  }
}

const themeStore = getThemeStore()

const themeConfig = computed(() => ({
  token: {
    colorPrimary: themeStore?.primaryColor || '#1890ff',
    borderRadius: 8,
    fontSize: 14
  },
  algorithm: themeStore?.isDark ? theme.darkAlgorithm : theme.defaultAlgorithm
}))
</script>

<style>
#app {
  min-height: 100vh;
}
</style>
