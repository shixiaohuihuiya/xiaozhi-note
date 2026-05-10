import { aiRequest } from './request'

// AI写作辅助
export const aiAssist = (data) => {
  return aiRequest.post('/ai/assist', null, { params: data })
}

// AI对话
export const aiChat = (data) => {
  return aiRequest.post('/ai/chat', null, { params: data })
}

// AI内容检查
export const aiCheck = (data) => {
  return aiRequest.post('/ai/check', null, { params: data })
}
