import request from './request'

export const getGuestbooks = (params) => {
  return request.get('/guestbooks', { params })
}

export const createGuestbook = (data) => {
  return request.post('/guestbooks', data)
}

export const likeGuestbook = (id) => {
  return request.post(`/guestbooks/${id}/like`)
}

export const deleteGuestbook = (id) => {
  return request.delete(`/guestbooks/${id}`)
}
