from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from schemas.chat import ChatRequest, ChatResponse, SaveChatHistoryRequest, Message
from services.ai_service import AIService
import config
from services.image_service import ImageService
from config import UPLOADS_DIR, CHAT_HISTORY_DIR
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json
import base64
import re
import shutil

# 创建一个 APIRouter 实例
router = APIRouter()

# 初始化服务
ai_service = AIService()
image_service = ImageService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    history: Optional[str] = Form(None)  # JSON字符串形式的历史记录
):
    """
    通用AI助手对话接口
    支持纯文本或文本+图片的多模态输入
    
    Args:
        message: 用户输入的文本消息
        image: 可选的图片文件
        history: 可选的历史对话记录（JSON字符串）
    
    Returns:
        ChatResponse: AI的回复（Markdown格式）
    """
    try:
        # 解析历史记录
        history_list = []
        if history:
            try:
                history_data = json.loads(history)
                # 转换为标准格式
                for msg in history_data:
                    history_list.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            except json.JSONDecodeError:
                print("[Chat API] 历史记录JSON解析失败")
        
        # 处理图片（如果有）
        image_path = None
        if image and image.filename:
            try:
                # 保存上传的图片
                image_content = await image.read()
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"chat_{timestamp}_{image.filename}"
                image_path = image_service.save_upload_file(image_content, filename)
                
                # 验证图片
                if not image_service.validate_image(image_path):
                    image_service.cleanup_file(image_path)
                    raise HTTPException(status_code=400, detail="无效的图片文件")
                
                print(f"[Chat API] 图片已保存: {image_path}")
            except Exception as e:
                print(f"[Chat API] 图片处理失败: {e}")
                raise HTTPException(status_code=500, detail=f"图片处理失败: {str(e)}")
        
        # 调用AI服务
        print(f"[Chat API] 用户消息: {message[:50]}...")
        print(f"[Chat API] 历史记录数量: {len(history_list)}")
        print(f"[Chat API] 是否包含图片: {image_path is not None}")
        
        # 根据是否有图片与可用密钥类型选择路线
        if image_path:
            # 有图片时必须使用 DashScope
            response_text = ai_service.chat_with_image(
                message=message,
                image_path=image_path,
                history=history_list
            )
        else:
            # 无图片：优先使用 ModelScope；若无 ModelScope 但有 DashScope，则走 DashScope 文本对话
            if config.MODELSCOPE_API_KEY:
                response_text = ai_service.chat(
                    message=message,
                    history=history_list
                )
            elif config.DASHSCOPE_API_KEY:
                response_text = ai_service.chat_with_image(
                    message=message,
                    image_path=None,
                    history=history_list
                )
            else:
                response_text = "抱歉，AI功能未配置。请联系管理员设置MODELSCOPE_API_KEY或DASHSCOPE_API_KEY。"
        
        # 清理临时图片文件（可选，也可以保留用于回顾）
        # if image_path:
        #     image_service.cleanup_file(image_path)
        
        return {"response": response_text}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Chat API] 对话异常: {e}")
        raise HTTPException(status_code=500, detail=f"对话处理失败: {str(e)}")

@router.post("/chat/save")
async def save_chat_history(request: SaveChatHistoryRequest):
    """
    保存聊天记录为Markdown文件
    
    Args:
        request: 包含完整对话历史的请求
    
    Returns:
        保存结果
    """
    try:
        # 生成文件名和assets文件夹
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}"
        md_filename = f"{filename}.md"
        assets_folder_name = f"{filename}.assets"
        
        file_path = CHAT_HISTORY_DIR / md_filename
        assets_dir = CHAT_HISTORY_DIR / assets_folder_name
        
        # 创建assets文件夹（如果需要）
        image_counter = 0
        
        # 生成Markdown内容
        md_content = f"""# 学习助手对话记录

**保存时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

"""
        
        # 添加对话内容
        for i, msg in enumerate(request.messages, 1):
            role_name = "👤 用户" if msg.role == "user" else "🤖 AI助手"
            md_content += f"## {role_name}\n\n"
            
            # 处理图片
            if msg.image_url:
                # 检查是否是base64编码的图片
                if msg.image_url.startswith('data:image'):
                    # 创建assets文件夹（仅在需要时创建）
                    if not assets_dir.exists():
                        assets_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 解析base64图片
                    try:
                        # 提取图片格式和数据
                        match = re.match(r'data:image/(\w+);base64,(.+)', msg.image_url)
                        if match:
                            image_format = match.group(1)
                            base64_data = match.group(2)
                            
                            # 解码base64数据
                            image_data = base64.b64decode(base64_data)
                            
                            # 保存图片
                            image_counter += 1
                            image_filename = f"image_{image_counter}.{image_format}"
                            image_path = assets_dir / image_filename
                            
                            with open(image_path, 'wb') as img_file:
                                img_file.write(image_data)
                            
                            # 在Markdown中引用图片（使用相对路径）
                            md_content += f"![图片](./{assets_folder_name}/{image_filename})\n\n"
                            print(f"[Chat API] 已保存图片: {image_path}")
                        else:
                            md_content += f"*[图片格式不支持]*\n\n"
                    except Exception as e:
                        print(f"[Chat API] 图片处理失败: {e}")
                        md_content += f"*[图片保存失败]*\n\n"
                        
                elif msg.image_url.startswith('http'):
                    # 如果是URL，直接引用
                    md_content += f"![图片]({msg.image_url})\n\n"
                else:
                    # 如果是本地文件路径，尝试复制
                    try:
                        source_path = Path(msg.image_url)
                        if source_path.exists() and source_path.is_file():
                            # 创建assets文件夹
                            if not assets_dir.exists():
                                assets_dir.mkdir(parents=True, exist_ok=True)
                            
                            image_counter += 1
                            # 保留原文件扩展名
                            ext = source_path.suffix
                            image_filename = f"image_{image_counter}{ext}"
                            image_path = assets_dir / image_filename
                            
                            # 复制文件
                            shutil.copy2(source_path, image_path)
                            
                            # 在Markdown中引用图片
                            md_content += f"![图片](./{assets_folder_name}/{image_filename})\n\n"
                            print(f"[Chat API] 已复制图片: {image_path}")
                        else:
                            md_content += f"*[图片文件不存在: {msg.image_url}]*\n\n"
                    except Exception as e:
                        print(f"[Chat API] 复制图片失败: {e}")
                        md_content += f"*[图片路径: {msg.image_url}]*\n\n"
            
            # 添加消息内容
            md_content += f"{msg.content}\n\n"
            md_content += "---\n\n"
        
        md_content += "*该对话记录由Study Helper自动生成*\n"
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"[Chat API] 聊天记录已保存: {file_path}")
        if image_counter > 0:
            print(f"[Chat API] 共保存 {image_counter} 张图片到: {assets_dir}")
        
        return {
            "message": "聊天记录已保存",
            "file_path": str(file_path),
            "filename": md_filename,
            "images_saved": image_counter
        }
        
    except Exception as e:
        print(f"[Chat API] 保存聊天记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")