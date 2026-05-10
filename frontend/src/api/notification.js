import request from './request'

export function getNotifications(params) {
  return request({
    url: '/notifications',
    method: 'get',
    params
  })
}

export function getUnreadCount() {
  return request({
    url: '/notifications/unread-count',
    method: 'get'
  })
}

export function markAsRead(notificationId) {
  return request({
    url: `/notifications/${notificationId}/read`,
    method: 'put'
  })
}

export function markAsUnread(notificationId) {
  return request({
    url: `/notifications/${notificationId}/unread`,
    method: 'put'
  })
}

export function deleteNotification(notificationId) {
  return request({
    url: `/notifications/${notificationId}`,
    method: 'delete'
  })
}

export function markAllAsRead() {
  return request({
    url: '/notifications/read-all',
    method: 'put'
  })
}

// ==================== Admin Notification APIs ====================

export function sendAdminNotification(data) {
  return request({
    url: '/notifications/admin/send',
    method: 'post',
    data
  })
}

export function getAdminNotifications(params) {
  return request({
    url: '/notifications/admin/list',
    method: 'get',
    params
  })
}

export function deleteAdminNotification(notificationId) {
  return request({
    url: `/notifications/admin/${notificationId}`,
    method: 'delete'
  })
}

export function getNotificationStats() {
  return request({
    url: '/notifications/admin/stats',
    method: 'get'
  })
}
