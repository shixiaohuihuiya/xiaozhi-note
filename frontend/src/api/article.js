import request from './request'

export const getArticles = (params) => {
  return request.get('/articles', { params })
}

export const getArticle = (slug) => {
  return request.get(`/articles/${slug}`)
}

export const createArticle = (data) => {
  return request.post('/articles', data)
}

export const updateArticle = (id, data) => {
  return request.put(`/articles/${id}`, data)
}

export const deleteArticle = (id) => {
  return request.delete(`/articles/${id}`)
}

export const getMyArticles = (params) => {
  return request.get('/users/me/articles', { params })
}

export const exportArticleMd = (articleId) => {
  return request.get(`/articles/${articleId}/export`, { responseType: 'blob' })
}
