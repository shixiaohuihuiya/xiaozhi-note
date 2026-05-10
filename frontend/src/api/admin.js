import request from './request'

// 用户管理
export const getAdminUsers = (params) => {
  return request.get('/admin/users', { params })
}

export const updateUserStatus = (id, status) => {
  return request.put(`/admin/users/${id}/status`, null, { params: { status } })
}

export const updateUserRole = (id, role) => {
  return request.put(`/admin/users/${id}/role`, null, { params: { role } })
}

export const resetUserPassword = (id) => {
  return request.put(`/admin/users/${id}/reset-password`)
}

export const createUser = (data) => {
  return request.post('/admin/users', null, { params: data })
}

export const updateUser = (id, data) => {
  return request.put(`/admin/users/${id}`, null, { params: data })
}

export const deleteUser = (id) => {
  return request.delete(`/admin/users/${id}`)
}

export const batchCreateUsers = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/admin/users/batch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const downloadUserTemplate = () => {
  return request.get('/admin/users/template', { responseType: 'blob' })
}

// 笔记管理
export const getAllArticles = (params) => {
  return request.get('/admin/articles', { params })
}

export const getPendingArticles = (params) => {
  return request.get('/admin/articles/pending', { params })
}

export const reviewArticle = (id, status, reason) => {
  return request.put(`/admin/articles/${id}/review`, null, { params: { status, reason } })
}

export const deleteArticle = (id) => {
  return request.delete(`/articles/${id}`)
}

// 评论管理
export const getAdminComments = (params) => {
  return request.get('/admin/comments', { params })
}

export const reviewComment = (id, status, reason) => {
  return request.put(`/admin/comments/${id}/review`, null, { params: { status, reason } })
}

export const deleteComment = (id) => {
  return request.delete(`/comments/${id}`)
}

// 仪表盘
export const getDashboardStats = () => {
  return request.get('/admin/dashboard')
}

// AI配置管理
export const getAiConfig = () => {
  return request.get('/config/ai')
}

export const updateAiConfig = (data) => {
  return request.put('/config/ai', data)
}

// 标签管理
export const getAdminTags = (params) => {
  return request.get('/tags', { params })
}

export const createTag = (data) => {
  return request.post('/tags', null, { params: data })
}

export const updateTag = (id, data) => {
  return request.put(`/tags/${id}`, null, { params: data })
}

export const deleteTag = (id) => {
  return request.delete(`/tags/${id}`)
}
