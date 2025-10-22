from pydantic import BaseModel
from typing import Optional, List, Dict

# 定义消息模型
class Message(BaseModel):
    """单条消息"""
    role: str  # 'user' 或 'assistant'
    content: str  # 消息内容
    image_url: Optional[str] = None  # 可选的图片URL（如果消息包含图片）

# 定义 ChatRequest 数据模型，用于验证进入的数据
class ChatRequest(BaseModel):
    """
    聊天请求
    支持纯文本或文本+图片的多模态输入
    """
    message: str  # 用户当前输入的消息
    history: Optional[List[Message]] = []  # 历史对话记录

# 定义 ChatResponse 数据模型，用于规范返回的数据
class ChatResponse(BaseModel):
    """聊天响应"""
    response: str  # AI的回复内容（Markdown格式）
    
# 保存聊天记录的请求
class SaveChatHistoryRequest(BaseModel):
    """保存聊天记录请求"""
    messages: List[Message]  # 完整的对话历史