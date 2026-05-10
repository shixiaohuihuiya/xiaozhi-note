import request from './request'

export const toggleLike = (articleId) => {
  return request.post(`/articles/${articleId}/like`)
}
