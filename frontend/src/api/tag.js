import request from './request'

export const getTags = () => {
  return request.get('/tags')
}

export const getTag = (id) => {
  return request.get(`/tags/${id}`)
}

export const createTag = (data) => {
  return request.post('/tags', data)
}

export const updateTag = (id, data) => {
  return request.put(`/tags/${id}`, data)
}

export const deleteTag = (id) => {
  return request.delete(`/tags/${id}`)
}
