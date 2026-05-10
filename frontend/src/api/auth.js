import request from './request'

export const login = (data) => {
  return request.post('/auth/login', data)
}

export const register = (data) => {
  return request.post('/auth/register', data)
}

export const getCaptcha = () => {
  return request.get('/auth/captcha')
}

export const getUserInfo = () => {
  return request.get('/users/me')
}

export const updateUserInfo = (data) => {
  return request.put('/users/me', data)
}

export const updatePassword = (data) => {
  return request.put('/users/me/password', data)
}
