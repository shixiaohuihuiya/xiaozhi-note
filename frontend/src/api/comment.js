import request from './request'

export const getArticleComments = (articleId, params = {}) => {
  return request.get(`/articles/${articleId}/comments`, { params })
}

export const createComment = (articleId, data) => {
  return request.post(`/articles/${articleId}/comments`, data)
}

export const deleteComment = (commentId) => {
  return request.delete(`/comments/${commentId}`)
}
