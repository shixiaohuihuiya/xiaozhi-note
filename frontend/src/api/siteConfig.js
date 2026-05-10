import request from './request'

export const getThemeConfig = () => {
  return request.get('/config/theme')
}

export const updateThemeConfig = (data) => {
  return request.put('/config/theme', data)
}

export const getSiteInfo = () => {
  return request.get('/config/info')
}

export const updateSiteInfo = (data) => {
  return request.put('/config/info', data)
}
