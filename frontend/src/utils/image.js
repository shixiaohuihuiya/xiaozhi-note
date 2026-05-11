/**
 * 图片URL工具函数
 */

/**
 * 获取完整的图片URL
 * @param {string} url - 图片相对路径或绝对路径
 * @returns {string} 完整的图片URL
 */
export const getImageUrl = (url) => {
  if (!url) return ''
  
  // 如果已经是完整URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  
  // 如果是相对路径，确保以 / 开头
  if (!url.startsWith('/')) {
    url = '/' + url
  }
  
  // 在生产环境（通过nginx访问），直接使用相对路径
  // nginx会正确代理 /uploads/ 到后端
  return url
}

/**
 * 获取API基础URL
 */
export const getApiBaseUrl = () => {
  return import.meta.env.VITE_API_BASE_URL || ''
}
