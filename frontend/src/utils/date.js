import dayjs from 'dayjs'

/**
 * 将后端返回的 UTC 时间字符串转换为本地时间显示
 * 后端使用 datetime.utcnow()，isoformat() 不带 Z，需要补 Z 再转本地
 */
export const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const utcStr = dateStr.includes('+') || dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
  return dayjs(utcStr).format('YYYY-MM-DD HH:mm')
}

export const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const utcStr = dateStr.includes('+') || dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
  return dayjs(utcStr).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * 相对时间显示（刚刚、几分钟前、几小时前、昨天、日期）
 */
export const formatRelativeTime = (dateStr) => {
  if (!dateStr) return '-'
  const utcStr = dateStr.includes('+') || dateStr.endsWith('Z') ? dateStr : dateStr + 'Z'
  const date = dayjs(utcStr)
  const now = dayjs()
  const diffMinutes = now.diff(date, 'minute')
  const diffHours = now.diff(date, 'hour')
  const diffDays = now.diff(date, 'day')

  if (diffMinutes < 1) return '刚刚'
  if (diffMinutes < 60) return `${diffMinutes}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays === 1) return '昨天 ' + date.format('HH:mm')
  if (diffDays < 7) return `${diffDays}天前`
  return date.format('YYYY-MM-DD HH:mm')
}
