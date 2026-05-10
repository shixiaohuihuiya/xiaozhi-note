import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getUserInfo } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  // 从 localStorage 恢复用户信息
  const savedUserInfo = localStorage.getItem('userInfo')
  const userInfo = ref(savedUserInfo ? JSON.parse(savedUserInfo) : null)
  
  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => userInfo.value?.role === 1 || userInfo.value?.role === 2)
  const isSuperadmin = computed(() => userInfo.value?.role === 2)
  
  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }
  
  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }
  
  const login = async (credentials) => {
    try {
      const res = await loginApi(credentials)
      if (res.code === 200) {
        setToken(res.data.access_token)
        userInfo.value = res.data.user
        // 保存 must_change_password 标记
        if (res.data.must_change_password) {
          userInfo.value.must_change_password = true
        }
        // 保存到 localStorage 以便刷新后恢复
        localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
      }
      return res
    } catch (error) {
      throw error
    }
  }
  
  const register = async (data) => {
    const res = await registerApi(data)
    return res
  }
  
  const fetchUserInfo = async () => {
    try {
      const res = await getUserInfo()
      if (res.code === 200) {
        userInfo.value = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
        return res.data
      }
    } catch (error) {
      clearToken()
      throw error
    }
  }

  const mustChangePassword = computed(() => !!userInfo.value?.must_change_password)
  
  const logout = () => {
    clearToken()
    // 清除 AI 聊天记录
    try {
      const keys = Object.keys(sessionStorage)
      keys.forEach(key => {
        if (key.startsWith('ai_chat_')) {
          sessionStorage.removeItem(key)
        }
      })
    } catch (e) {
      // ignore
    }
  }
  
  return {
    token,
    userInfo,
    isLoggedIn,
    isAdmin,
    isSuperadmin,
    mustChangePassword,
    login,
    register,
    fetchUserInfo,
    logout
  }
})
