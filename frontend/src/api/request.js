import axios from 'axios'
import { message } from 'ant-design-vue'
import { useUserStore } from '@/stores/user'

// 创建axios实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// AI专用实例（超时时间较长）
const aiRequest = axios.create({
  baseURL: '/api/v1',
  timeout: 180000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 获取 token 的辅助函数
const getToken = () => {
  try {
    const userStore = useUserStore()
    return userStore.token
  } catch (e) {
    // Pinia 未初始化，从 localStorage 读取
    return localStorage.getItem('token') || ''
  }
}

// 通用请求拦截器
const attachToken = (config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

request.interceptors.request.use(attachToken, (error) => Promise.reject(error))
aiRequest.interceptors.request.use(attachToken, (error) => Promise.reject(error))

// 响应拦截器
const attachResponseInterceptor = (instance) => {
  instance.interceptors.response.use(
    (response) => {
      const res = response.data
      if (res.code === undefined) {
        return res
      }
      if (res.code !== 200) {
        if (res.code === 401) {
          try {
            const userStore = useUserStore()
            userStore.logout()
          } catch (e) {
            localStorage.removeItem('token')
          }
          window.location.href = '/login'
        }
        return Promise.reject({ message: res.message || '请求失败', code: res.code })
      }
      return res
    },
    (error) => {
      const { response } = error
      if (response) {
        const { status, data } = response
        switch (status) {
          case 401:
            message.error('登录已过期，请重新登录')
            try {
              const userStore = useUserStore()
              userStore.logout()
            } catch (e) {
              localStorage.removeItem('token')
            }
            window.location.href = '/login'
            break
          case 403:
            message.error(data?.detail || '没有权限执行此操作')
            break
          case 404:
            message.error('请求的资源不存在')
            break
          case 503:
            message.error(data?.detail || 'AI服务暂不可用')
            break
          case 500:
            message.error('服务器内部错误')
            break
          default:
            message.error(data?.message || data?.detail || '请求失败')
        }
      } else {
        if (error.code === 'ECONNABORTED') {
          message.error('请求超时，AI处理时间较长请稍后重试')
        } else {
          message.error('网络错误，请检查网络连接')
        }
      }
      return Promise.reject(error)
    }
  )
}

attachResponseInterceptor(request)
attachResponseInterceptor(aiRequest)

export default request
export { aiRequest }
