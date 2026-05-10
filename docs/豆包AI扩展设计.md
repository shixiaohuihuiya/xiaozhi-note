# 小智笔记 - 豆包AI扩展功能设计

---

## 1. 功能概述

豆包AI扩展是小智笔记的核心特色功能，通过与字节跳动豆包大模型API集成，为用户提供智能写作辅助、内容优化、智能问答等服务，帮助用户提升写作效率和内容质量。

---

## 2. 功能架构

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  文章编辑器  │  │ AI侧边栏助手 │  │ 快捷指令面板        │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      FastAPI 后端                           │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    AI服务层 (ai_service.py)            │ │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │ │
│  │  │ 写作辅助服务  │ │ 智能问答服务  │ │ 内容检查服务  │  │ │
│  │  └──────────────┘ └──────────────┘ └──────────────┘  │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                    对话管理服务                         │ │
│  │  - 会话管理  - 上下文维护  - 历史记录存储              │ │
│  └───────────────────────────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                      豆包API接口层                          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │              字节跳动豆包大模型 API                    │ │
│  │  - 豆包-pro (专业版)  - 豆包-lite (轻量版)            │ │
│  │  - 流式响应  - Function Calling  - 多轮对话          │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 核心功能模块

### 3.1 AI写作辅助

#### 3.1.1 文章续写

**功能描述**: 根据已有内容，智能生成后续段落。

**使用场景**:
- 写作卡壳时获取灵感
- 快速扩展文章篇幅
- 保持文章风格一致性

**输入参数**:
```json
{
  "action": "continue",
  "title": "文章标题",
  "content": "已写的内容...",
  "tone": "professional",  // 语气: casual/professional/academic
  "length": "medium"       // 长度: short/medium/long
}
```

**输出示例**:
```json
{
  "result": "续写的内容...",
  "suggestions": ["建议1", "建议2"],
  "confidence": 0.92
}
```

---

#### 3.1.2 文章润色

**功能描述**: 优化语言表达，提升文章质量。

**润色类型**:
| 类型 | 说明 |
|------|------|
| grammar | 语法修正 |
| style | 风格优化 |
| concise | 精简表达 |
| vivid | 生动化 |
| academic | 学术化 |

**输入参数**:
```json
{
  "action": "polish",
  "content": "需要润色的段落",
  "polish_type": "style",
  "preserve_meaning": true
}
```

---

#### 3.1.3 内容扩写

**功能描述**: 将简短内容扩展为详细论述。

**输入参数**:
```json
{
  "action": "expand",
  "content": "核心观点",
  "target_length": 500,  // 目标字数
  "add_examples": true,  // 是否添加例子
  "add_data": false      // 是否添加数据支撑
}
```

---

#### 3.1.4 标题生成

**功能描述**: 根据文章内容生成吸引人的标题。

**标题风格**:
| 风格 | 示例 |
|------|------|
| clickbait | "震惊！程序员竟然..." |
| professional | "Python异步编程最佳实践" |
| question | "如何写出高质量的技术文章？" |
| list | "10个提升代码质量的小技巧" |

**输入参数**:
```json
{
  "action": "title",
  "content": "文章内容摘要",
  "count": 5,           // 生成数量
  "style": "professional"
}
```

**输出示例**:
```json
{
  "titles": [
    "深入浅出：FastAPI异步编程完全指南",
    "FastAPI性能优化：从入门到精通",
    "构建高性能API：FastAPI实战技巧"
  ]
}
```

---

#### 3.1.5 摘要生成

**功能描述**: 自动生成文章摘要。

**输入参数**:
```json
{
  "action": "summary",
  "content": "完整文章内容",
  "max_length": 200,    // 最大字数
  "style": "abstract"   // 风格: abstract/key_points/narrative
}
```

---

### 3.2 AI智能问答助手

#### 3.2.1 侧边栏AI助手

**功能描述**: 在编辑器侧边栏提供实时AI对话功能。

**界面设计**:
```
┌─────────────────────────────────────────────────────────┐
│  文章编辑器                              │  🤖 AI助手   │
│                                         │ ──────────── │
│  # 文章标题                              │ 你好！我是   │
│                                         │ 小智AI，可以 │
│  文章内容...                             │ 帮你写作。   │
│                                         │              │
│                                         │ ──────────── │
│                                         │ 快捷指令:    │
│                                         │ [续写] [润色]│
│                                         │ [纠错] [扩写]│
│                                         │              │
│                                         │ ──────────── │
│                                         │ 对话历史...  │
│                                         │              │
│                                         │ ┌──────────┐ │
│                                         │ │输入消息...│ │
│                                         │ └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

#### 3.2.2 上下文感知对话

**功能描述**: AI能够理解当前编辑的文章内容，提供上下文相关的回答。

**上下文类型**:
| 类型 | 说明 |
|------|------|
| current_paragraph | 当前段落 |
| selected_text | 选中文本 |
| full_article | 完整文章 |
| cursor_position | 光标位置 |

**请求示例**:
```json
{
  "message": "这段话写得怎么样？",
  "context": {
    "type": "selected_text",
    "content": "选中的文本内容",
    "article_id": 123,
    "position": "第3段"
  },
  "session_id": "sess_abc123"
}
```

---

#### 3.2.3 快捷指令

**预设指令列表**:

| 指令 | 功能 | 快捷键 |
|------|------|--------|
| /continue | 续写当前段落 | Ctrl+Shift+C |
| /polish | 润色选中文本 | Ctrl+Shift+P |
| /expand | 扩写选中文本 | Ctrl+Shift+E |
| /fix | 修正语法错误 | Ctrl+Shift+F |
| /title | 生成标题建议 | Ctrl+Shift+T |
| /summary | 生成摘要 | Ctrl+Shift+S |
| /help | 获取写作建议 | Ctrl+Shift+H |

---

### 3.3 内容检查与纠错

#### 3.3.1 语法检查

**功能描述**: 自动检测文章中的语法错误。

**检测项**:
- 错别字
- 标点符号使用
- 语法结构
- 用词不当

**输出格式**:
```json
{
  "has_errors": true,
  "error_count": 3,
  "suggestions": [
    {
      "type": "spelling",
      "position": {"line": 5, "column": 12},
      "original": "程序猿",
      "suggestion": "程序员",
      "explanation": "建议使用规范用词"
    },
    {
      "type": "punctuation",
      "position": {"line": 8, "column": 45},
      "original": "，",
      "suggestion": "。",
      "explanation": "句子结束应使用句号"
    }
  ]
}
```

---

#### 3.3.2 敏感词检测

**功能描述**: 检测文章中的敏感内容。

**检测级别**:
| 级别 | 处理方式 |
|------|----------|
| info | 提示建议 |
| warning | 警告提醒 |
| error | 必须修改 |

---

## 4. 技术实现

### 4.1 FastAPI 服务实现

```python
# app/services/ai_service.py

from typing import Optional, List, Dict, Any
from openai import AsyncOpenAI
from config import settings

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DOUBAO_API_KEY,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        self.model = settings.DOUBAO_MODEL  # "doubao-pro-32k"
    
    async def assist_writing(
        self,
        action: str,
        content: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """AI写作辅助"""
        
        prompts = {
            "continue": f"请根据以下内容续写，保持风格一致:\n\n{content}",
            "polish": f"请润色以下文本，使其更加流畅和专业:\n\n{content}",
            "expand": f"请将以下内容扩写得更详细:\n\n{content}",
            "title": f"请为以下内容生成5个吸引人的标题:\n\n{content}",
            "summary": f"请为以下内容生成摘要:\n\n{content}"
        }
        
        prompt = prompts.get(action, content)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位专业的写作助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            "result": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """AI对话"""
        
        messages = []
        
        # 添加上下文
        if context:
            context_msg = f"当前上下文: {context.get('type')} - {context.get('content', '')[:500]}"
            messages.append({"role": "system", "content": context_msg})
        
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8,
            stream=False
        )
        
        return {
            "reply": response.choices[0].message.content,
            "session_id": session_id or self._generate_session_id(),
            "tokens_used": response.usage.total_tokens
        }
    
    async def check_content(self, content: str) -> Dict[str, Any]:
        """内容检查"""
        
        prompt = f"""请检查以下文本的语法和用词错误，以JSON格式返回：

文本：{content}

请返回格式：
{{
  "has_errors": true/false,
  "suggestions": [
    {{
      "type": "spelling/grammar/punctuation",
      "position": "位置描述",
      "original": "原文",
      "suggestion": "建议修改",
      "explanation": "说明"
    }}
  ]
}}"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        # 解析JSON响应
        import json
        try:
            result = json.loads(response.choices[0].message.content)
            return result
        except:
            return {"has_errors": False, "suggestions": []}
    
    def _generate_session_id(self) -> str:
        import uuid
        return f"sess_{uuid.uuid4().hex[:12]}"


# 创建服务实例
ai_service = AIService()
```

---

### 4.2 API路由实现

```python
# app/routers/ai.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from services.ai_service import ai_service
from dependencies.auth import get_current_user
from models import User

router = APIRouter()

class AIAssistRequest(BaseModel):
    action: str  # continue, polish, expand, title, summary
    content: str
    context: Optional[str] = None
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"

class AIChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    article_id: Optional[int] = None
    context: Optional[dict] = None

class AICheckRequest(BaseModel):
    content: str

@router.post("/assist")
async def ai_assist(
    request: AIAssistRequest,
    current_user: User = Depends(get_current_user)
):
    """AI写作辅助"""
    try:
        result = await ai_service.assist_writing(
            action=request.action,
            content=request.content,
            context=request.context,
            tone=request.tone,
            length=request.length
        )
        
        # 保存AI对话记录
        await save_conversation(
            user_id=current_user.id,
            session_id=request.session_id,
            action=request.action,
            result=result
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def ai_chat(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user)
):
    """AI智能问答"""
    try:
        result = await ai_service.chat(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        
        # 保存对话记录
        await save_conversation(
            user_id=current_user.id,
            session_id=result["session_id"],
            article_id=request.article_id,
            user_message=request.message,
            ai_reply=result["reply"],
            tokens_used=result["tokens_used"]
        )
        
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check")
async def ai_check(
    request: AICheckRequest,
    current_user: User = Depends(get_current_user)
):
    """AI内容检查"""
    try:
        result = await ai_service.check_content(request.content)
        return {
            "code": 200,
            "message": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/conversations")
async def get_conversations(
    session_id: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user)
):
    """获取AI对话历史"""
    # 查询数据库获取对话记录
    pass

async def save_conversation(**kwargs):
    """保存对话记录到数据库"""
    # 实现保存逻辑
    pass
```

---

### 4.3 配置文件

```python
# app/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "mysql+aiomysql://user:pass@localhost/xiaozhi_notes"
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT配置
    JWT_SECRET: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24
    
    # 豆包AI配置
    DOUBAO_API_KEY: str = "your-doubao-api-key"
    DOUBAO_MODEL: str = "doubao-pro-32k"
    DOUBAO_LITE_MODEL: str = "doubao-lite-32k"
    
    # AI功能开关
    AI_ENABLED: bool = True
    AI_MAX_TOKENS_PER_REQUEST: int = 4000
    AI_DAILY_LIMIT_PER_USER: int = 100
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 5. 前端集成

### 5.1 AI助手组件

```vue
<!-- frontend/src/components/AIAssistant.vue -->
<template>
  <div class="ai-assistant">
    <div class="ai-header">
      <span class="ai-icon">🤖</span>
      <span class="ai-title">AI助手</span>
    </div>
    
    <div class="ai-quick-actions">
      <button 
        v-for="action in quickActions" 
        :key="action.key"
        @click="handleQuickAction(action.key)"
        class="action-btn"
      >
        {{ action.label }}
      </button>
    </div>
    
    <div class="ai-chat" ref="chatContainer">
      <div 
        v-for="msg in messages" 
        :key="msg.id"
        :class="['message', msg.role === 'user' ? 'user' : 'ai']"
      >
        <div class="message-content">{{ msg.content }}</div>
        <div class="message-time">{{ formatTime(msg.created_at) }}</div>
      </div>
    </div>
    
    <div class="ai-input">
      <textarea
        v-model="inputMessage"
        @keydown.enter.prevent="sendMessage"
        placeholder="输入消息或 / 查看快捷指令..."
        rows="3"
      />
      <button @click="sendMessage" :disabled="loading">
        {{ loading ? '发送中...' : '发送' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAIStore } from '@/stores/ai'

const props = defineProps({
  articleId: Number,
  selectedText: String
})

const aiStore = useAIStore()
const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const sessionId = ref('')

const quickActions = [
  { key: 'continue', label: '✍️ 续写' },
  { key: 'polish', label: '✨ 润色' },
  { key: 'expand', label: '📖 扩写' },
  { key: 'fix', label: '🔧 纠错' }
]

const handleQuickAction = async (action) => {
  const content = props.selectedText || ''
  if (!content && action !== 'continue') {
    alert('请先选择要处理的文本')
    return
  }
  
  loading.value = true
  try {
    const result = await aiStore.assistWriting({
      action,
      content,
      article_id: props.articleId
    })
    
    messages.value.push({
      role: 'ai',
      content: result.data.result,
      created_at: new Date()
    })
  } finally {
    loading.value = false
  }
}

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return
  
  const message = inputMessage.value
  inputMessage.value = ''
  
  messages.value.push({
    role: 'user',
    content: message,
    created_at: new Date()
  })
  
  loading.value = true
  try {
    const result = await aiStore.chat({
      message,
      session_id: sessionId.value,
      article_id: props.articleId,
      context: {
        type: 'selected_text',
        content: props.selectedText
      }
    })
    
    sessionId.value = result.data.session_id
    messages.value.push({
      role: 'ai',
      content: result.data.reply,
      created_at: new Date()
    })
  } finally {
    loading.value = false
  }
}
</script>
```

---

### 5.2 AI Store (Pinia)

```typescript
// frontend/src/stores/ai.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useAIStore = defineStore('ai', () => {
  const conversations = ref([])
  const loading = ref(false)
  
  const assistWriting = async (params: {
    action: string
    content: string
    article_id?: number
    context?: string
  }) => {
    loading.value = true
    try {
      const response = await axios.post('/api/v1/ai/assist', params)
      return response.data
    } finally {
      loading.value = false
    }
  }
  
  const chat = async (params: {
    message: string
    session_id?: string
    article_id?: number
    context?: object
  }) => {
    loading.value = true
    try {
      const response = await axios.post('/api/v1/ai/chat', params)
      return response.data
    } finally {
      loading.value = false
    }
  }
  
  const checkContent = async (content: string) => {
    const response = await axios.post('/api/v1/ai/check', { content })
    return response.data
  }
  
  return {
    conversations,
    loading,
    assistWriting,
    chat,
    checkContent
  }
})
```

---

## 6. 使用限制与配额

### 6.1 用户配额管理

| 用户类型 | 每日请求次数 | 单次最大Token |
|----------|-------------|--------------|
| 普通用户 | 50次 | 2000 |
| VIP用户 | 200次 | 4000 |
| 管理员 | 无限制 | 4000 |

### 6.2 限流配置

```python
from fastapi import Request
from fastapi_limiter.depends import RateLimiter

# 路由限流
@router.post("/assist", dependencies=[Depends(RateLimiter(times=10, minutes=1))])
async def ai_assist(...):
    pass
```

---

## 7. 错误处理

### 7.1 常见错误码

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| AI001 | API密钥无效 | 检查配置 |
| AI002 | 请求频率过高 | 稍后重试 |
| AI003 | 内容过长 | 分段处理 |
| AI004 | 服务暂不可用 | 使用离线模式 |
| AI005 | 配额已用完 | 提示用户升级 |

---

## 8. 隐私与安全

### 8.1 数据处理原则

1. **不存储敏感内容**: AI对话仅保存元数据，不保存完整内容
2. **用户控制**: 用户可删除自己的AI对话历史
3. **传输加密**: 所有API请求使用HTTPS
4. **访问控制**: 只能访问自己的AI对话记录

### 8.2 内容过滤

```python
# 敏感内容过滤
FORBIDDEN_TOPICS = [
    "政治敏感内容",
    "违法信息",
    "个人隐私"
]

def content_filter(text: str) -> bool:
    """检查内容是否合规"""
    for topic in FORBIDDEN_TOPICS:
        if topic in text:
            return False
    return True
```

---

**文档版本**: v1.0  
**创建日期**: 2026-04-13  
**AI模型**: 豆包-pro-32k / 豆包-lite-32k
