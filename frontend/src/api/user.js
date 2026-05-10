import request from './request'

export const getUsers = (params) => {
  return request.get('/users', { params })
}

export const getAllUsers = () => {
  return request.get('/users/all')
}

export const getUser = (id) => {
  return request.get(`/users/${id}`)
}

export const updateUser = (id, data) => {
  return request.put(`/users/${id}`, data)
}

export const deleteUser = (id) => {
  return request.delete(`/users/${id}`)
}

export const updateCurrentUser = (data) => {
  return request.put('/users/me', data)
}

export const updatePassword = (data) => {
  return request.put('/users/me/password', data)
}
