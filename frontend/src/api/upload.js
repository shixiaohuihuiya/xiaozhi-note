import request from './request'

export const uploadImage = (file, usageType = 1, articleId = null) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post(`/uploads/image?usage_type=${usageType}${articleId ? `&article_id=${articleId}` : ''}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const getUploadedImages = (params) => {
  return request.get('/uploads/images', { params })
}

export const deleteUpload = (id) => {
  return request.delete(`/uploads/${id}`)
}
