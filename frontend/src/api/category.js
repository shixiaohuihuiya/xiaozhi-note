import request from './request'

export const getCategories = () => {
  return request.get('/categories')
}

export const getCategory = (id) => {
  return request.get(`/categories/${id}`)
}

export const createCategory = (data) => {
  return request.post('/categories', data)
}

export const updateCategory = (id, data) => {
  return request.put(`/categories/${id}`, data)
}

export const deleteCategory = (id) => {
  return request.delete(`/categories/${id}`)
}
