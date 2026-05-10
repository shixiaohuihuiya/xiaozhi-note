"""
AI服务 - 豆包AI集成
"""
import json
import uuid
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from config import settings


class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.client = None
        if settings.DOUBAO_API_KEY:
            self.client = AsyncOpenAI(
                api_key=settings.DOUBAO_API_KEY,
                base_url=settings.DOUBAO_BASE_URL,
                timeout=180.0
            )
        self.model = settings.DOUBAO_MODEL
    
    async def assist_writing(
        self,
        action: str,
        content: str,
        context: Optional[str] = None,
        tone: str = "professional",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        AI写作辅助
        
        Args:
            action: 操作类型 (continue, polish, expand, title, summary)
            content: 当前内容
            context: 上下文信息
            tone: 语气风格
            length: 长度
            
        Returns:
            Dict: 包含result和tokens_used
        """
        if not self.client:
            raise Exception("AI服务未配置")
        
        # 构建提示词
        prompts = {
            "continue": f"请根据以下内容续写，保持风格一致:\n\n{content}",
            "polish": f"请润色以下文本，使其更加流畅和专业:\n\n{content}",
            "expand": f"请将以下内容扩写得更详细，增加例子和说明:\n\n{content}",
            "title": f"请为以下内容生成5个吸引人的标题，用换行分隔:\n\n{content}",
            "summary": f"请为以下内容生成简洁的摘要:\n\n{content}"
        }
        
        prompt = prompts.get(action, content)
        
        if context:
            prompt = f"上下文: {context}\n\n{prompt}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位专业的写作助手，擅长帮助用户改进文章质量。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=settings.AI_MAX_TOKENS_PER_REQUEST
        )
        
        return {
            "result": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
    
    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        AI对话
        
        Args:
            message: 用户消息
            session_id: 会话ID
            context: 上下文信息
            
        Returns:
            Dict: 包含reply, session_id和tokens_used
        """
        if not self.client:
            raise Exception("AI服务未配置")
        
        messages = [
            {"role": "system", "content": "你是小智笔记的AI助手，专门帮助用户进行写作和知识管理。"}
        ]
        
        # 添加上下文
        if context:
            context_msg = f"当前编辑的{context.get('type', '内容')}: {context.get('content', '')[:500]}"
            messages.append({"role": "system", "content": context_msg})
        
        messages.append({"role": "user", "content": message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.8,
            max_tokens=settings.AI_MAX_TOKENS_PER_REQUEST
        )
        
        return {
            "reply": response.choices[0].message.content,
            "session_id": session_id or self._generate_session_id(),
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
    
    async def check_content(self, content: str) -> Dict[str, Any]:
        """
        内容检查
        
        Args:
            content: 需要检查的文本
            
        Returns:
            Dict: 检查结果和建议
        """
        if not self.client:
            raise Exception("AI服务未配置")
        
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
            temperature=0.3,
            max_tokens=2000
        )
        
        # 解析JSON响应
        try:
            result_text = response.choices[0].message.content
            # 提取JSON部分
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            return result
        except Exception:
            return {"has_errors": False, "suggestions": []}
    
    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"sess_{uuid.uuid4().hex[:12]}"


# 创建服务实例
ai_service = AIService()
