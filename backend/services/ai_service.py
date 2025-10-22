"""
AI服务模块 - 基于ModelScope API
参考文档: https://modelscope.cn/docs/model-service/API-Inference/intro
"""
import requests
import json
import base64
from pathlib import Path
from typing import Dict, Optional
import config
from prompts import (
    OCR_PROMPT,
    ESSAY_OPTIMIZATION_PROMPT,
    SMALL_ESSAY_OPTIMIZATION_PROMPT,
    LARGE_ESSAY_OPTIMIZATION_PROMPT,
    STRUCTURE_VALIDATION_PROMPT,
    CHAT_SYSTEM_PROMPT
)

class AIService:
    """AI服务类，使用ModelScope API"""
    
    def __init__(self, api_key: str = None):
        """
        初始化AI服务
        
        Args:
            api_key: ModelScope API密钥
        """
        self.api_key = api_key or config.MODELSCOPE_API_KEY
        # 使用配置中的端点，避免在代码中硬编码 URL
        self.api_url = config.MODELSCOPE_API_BASE
        
        if not self.api_key:
            print("[WARNING] 未配置MODELSCOPE_API_KEY，AI功能将使用占位符")
    
    def _get_modelscope_key(self) -> Optional[str]:
        """获取最新的ModelScope密钥（优先实例自带，其次全局配置）"""
        return self.api_key or config.MODELSCOPE_API_KEY
    
    def _get_dashscope_key(self) -> Optional[str]:
        """获取最新的DashScope密钥（优先全局配置，其次实例自带）"""
        return config.DASHSCOPE_API_KEY or self.api_key
    
    def _call_modelscope_api(
        self, 
        model: str, 
        messages: list, 
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        调用ModelScope API的通用方法
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            模型返回的文本内容，失败返回None
        """
        api_key = self._get_modelscope_key()
        if not api_key:
            return None
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'  # 使用Bearer认证
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            print(f"[AI Service] 调用模型: {model}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"[AI Service] API返回错误: {response.status_code}")
                print(f"[AI Service] 错误详情: {response.text}")
                return None
            
            result = response.json()
            
            # 提取返回内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return content
            else:
                print(f"[AI Service] 响应格式异常: {result}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[AI Service] API调用超时")
            return None
        except Exception as e:
            print(f"[AI Service] API调用异常: {e}")
            return None
    
    def image_to_text(self, image_path: str, prompt: str = "") -> str:
        """
        将图像转换为文本（OCR）
        
        使用 Qwen3-VL-Thinking 多模态思考模型进行图像识别
        
        Args:
            image_path: 图像文件路径
            prompt: 自定义提示词（可选）
            
        Returns:
            识别出的文本内容
        """
        if not self._get_modelscope_key():
            print("[AI Service] 使用占位符 - OCR识别")
            return self._get_placeholder_ocr_result()
        
        try:
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # 使用配置文件中的提示词
            if not prompt:
                prompt = OCR_PROMPT
            
            # 根据 Qwen3-VL 官方文档格式构建消息
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        }
                    ]
                }
            ]
            
            # 调用 Qwen3-VL-Thinking 多模态思考模型
            result = self._call_modelscope_api(
                model=config.VISION_MODEL,
                messages=messages,
                temperature=0.1,  # 低温度，更准确的识别
                max_tokens=2000
            )
            
            if result:
                print(f"[AI Service] OCR识别成功，文本长度: {len(result)}")
                return result
            else:
                print("[AI Service] OCR识别失败，使用占位符")
                return self._get_placeholder_ocr_result()
                
        except Exception as e:
            print(f"[AI Service] OCR处理异常: {e}")
            return self._get_placeholder_ocr_result()
    
    def optimize_essay(
        self, 
        topic_image_path: str,
        reference: str, 
        original: str,
        essay_type: str = "",
        prompt: str = ""
    ) -> Dict:
        """
        优化作文并生成建议
        
        Args:
            topic_image_path: 作文题目图片路径
            reference: 参考范文
            original: 学生原文
            essay_type: 作文类型（'小作文' 或 '大作文'）
            prompt: 自定义提示词（可选）
            
        Returns:
            包含优化文本和建议的字典
        """
        if not self._get_modelscope_key():
            print("[AI Service] 使用占位符 - 作文优化")
            return self._get_placeholder_optimization()
        
        try:
            # 读取题目图片并转换为base64
            topic_image_base64 = None
            if topic_image_path and Path(topic_image_path).exists():
                with open(topic_image_path, 'rb') as f:
                    topic_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 使用配置文件中的提示词，并填充变量
            if not prompt:
                # 根据作文类型选择不同的提示词
                if essay_type == "小作文":
                    prompt_template = SMALL_ESSAY_OPTIMIZATION_PROMPT
                elif essay_type == "大作文":
                    prompt_template = LARGE_ESSAY_OPTIMIZATION_PROMPT
                else:
                    prompt_template = ESSAY_OPTIMIZATION_PROMPT
                
                # 不再在提示词中填充topic（因为是图片），只填充其他变量
                prompt_text = f"""{prompt_template.split('【作文题目】')[0]}

【作文题目】
见上方题目图片

【参考范文】
{reference}

【学生原文】
{original}

{prompt_template.split('【学生原文】')[1].split('{original}')[1] if '{original}' in prompt_template else ''}"""
            else:
                prompt_text = prompt
            
            # 构建消息（使用 Qwen3-VL-Thinking 多模态思考模型）
            if topic_image_base64:
                # 多模态输入：题目图片 + 文字说明
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请仔细分析以下英语作文。首先查看题目图片，理解题目要求："
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{topic_image_base64}"}
                            },
                            {
                                "type": "text",
                                "text": prompt_text
                            }
                        ]
                    }
                ]
            else:
                # 纯文本输入（兼容没有题目图片的情况）
                messages = [
                    {"role": "user", "content": prompt_text}
                ]
            
            # 统一使用 Qwen3-VL-Thinking 多模态思考模型
            # 这个模型结合了视觉理解和深度思考能力，非常适合作文优化任务
            result = self._call_modelscope_api(
                model=config.VISION_MODEL,
                messages=messages,
                temperature=0.5,  # 适中温度，平衡准确性和创造性
                max_tokens=4000   # 增加token限制，给模型更多思考和输出空间
            )
            
            if not result:
                print("[AI Service] 作文优化失败，使用占位符")
                return self._get_placeholder_optimization()
            
            # 解析JSON返回
            try:
                # 提取JSON（有时模型会在前后加说明文字）
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    parsed_result = json.loads(json_str)
                    
                    # 验证结构
                    if self._validate_optimization_structure(parsed_result):
                        print("[AI Service] 作文优化成功")
                        return parsed_result
                    else:
                        print("[AI Service] 返回结构不完整，使用占位符")
                        return self._get_placeholder_optimization()
                else:
                    print("[AI Service] 无法提取JSON，使用占位符")
                    return self._get_placeholder_optimization()
                    
            except json.JSONDecodeError as e:
                print(f"[AI Service] JSON解析失败: {e}")
                print(f"[AI Service] 原始返回: {result[:200]}...")
                return self._get_placeholder_optimization()
                
        except Exception as e:
            print(f"[AI Service] 作文优化异常: {e}")
            return self._get_placeholder_optimization()
    
    def optimize_essay_with_images(
        self,
        topic_image_path: str,
        essay_image_path: str,
        reference: str,
        essay_type: str = ""
    ) -> Dict:
        """
        使用 Qwen3-VL-Thinking 一次性处理题目图片和作文图片
        
        这个方法充分发挥多模态模型的能力，同时"看到"题目和作文，
        进行更准确的分析和优化。
        
        Args:
            topic_image_path: 题目图片路径
            essay_image_path: 学生作文图片路径
            reference: 参考范文
            essay_type: 作文类型（'小作文' 或 '大作文'）
            
        Returns:
            包含优化文本和建议的字典
        """
        if not self._get_modelscope_key():
            print("[AI Service] 使用占位符 - 多模态作文优化")
            return self._get_placeholder_optimization()
        
        try:
            # 读取题目图片
            topic_image_base64 = None
            if topic_image_path and Path(topic_image_path).exists():
                with open(topic_image_path, 'rb') as f:
                    topic_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 读取作文图片
            essay_image_base64 = None
            if essay_image_path and Path(essay_image_path).exists():
                with open(essay_image_path, 'rb') as f:
                    essay_image_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # 根据作文类型选择提示词
            if essay_type == "小作文":
                prompt_template = SMALL_ESSAY_OPTIMIZATION_PROMPT
            elif essay_type == "大作文":
                prompt_template = LARGE_ESSAY_OPTIMIZATION_PROMPT
            else:
                prompt_template = ESSAY_OPTIMIZATION_PROMPT
            
            # 构建提示词（去掉原文部分，因为会从图片识别）
            base_prompt = prompt_template.split('【学生原文】')[0]
            instruction = prompt_template.split('【学生原文】')[1] if '【学生原文】' in prompt_template else ''
            
            prompt_text = f"""{base_prompt}

【参考范文】
{reference}

以下是题目图片和学生手写作文图片，请按以下步骤分析：

1. **仔细查看题目图片**，理解题目要求、格式和评分标准
2. **识别学生手写作文**的所有内容（严格保留原文中的所有拼写和语法错误，不要修正）
3. **对照题目和参考范文**进行深度分析
4. **提供优化建议**

你必须返回严格的JSON格式，包含以下字段（非常重要）：
{{
    "original_text": "识别出的学生原文（保留所有错误）",
    "optimized_text": "优化后的完整作文内容",
    "suggestions": {{
        "topic_compliance": ["关于主题贴合度的分析和建议"],
        "spelling_errors": ["拼写错误列表"],
        "grammar_errors": ["语法错误列表"],
        "word_optimization": ["词汇优化建议"],
        "sentence_optimization": ["句子优化建议"],
        "structure_optimization": ["文章结构优化建议"]
    }}
}}

{instruction}

请确保返回的是有效的JSON格式，不要包含任何额外的文字说明。"""
            
            # 构建多模态消息
            content = [
                {"type": "text", "text": "【题目图片】请先查看作文题目："}
            ]
            
            if topic_image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{topic_image_base64}"}
                })
            
            content.append({"type": "text", "text": "\n【学生作文图片】以下是学生的手写作文："})
            
            if essay_image_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{essay_image_base64}"}
                })
            
            content.append({"type": "text", "text": f"\n{prompt_text}"})
            
            messages = [{"role": "user", "content": content}]
            
            # 调用 Qwen3-VL-Thinking 多模态思考模型
            print(f"[AI Service] 使用 Qwen3-VL-Thinking 进行多模态分析")
            result = self._call_modelscope_api(
                model=config.VISION_MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=5000  # 更大的输出空间
            )
            
            if not result:
                print("[AI Service] 多模态优化失败，使用占位符")
                return self._get_placeholder_optimization()
            
            # 解析JSON返回
            try:
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    parsed_result = json.loads(json_str)
                    
                    if self._validate_optimization_structure(parsed_result):
                        print("[AI Service] 多模态作文优化成功")
                        return parsed_result
                    else:
                        print("[AI Service] 返回结构不完整，使用占位符")
                        return self._get_placeholder_optimization()
                else:
                    print("[AI Service] 无法提取JSON，使用占位符")
                    return self._get_placeholder_optimization()
                    
            except json.JSONDecodeError as e:
                print(f"[AI Service] JSON解析失败: {e}")
                return self._get_placeholder_optimization()
                
        except Exception as e:
            print(f"[AI Service] 多模态优化异常: {e}")
            return self._get_placeholder_optimization()
    
    def validate_structure(self, data: Dict) -> bool:
        """
        使用AI验证数据结构
        
        Args:
            data: 待验证的数据
            
        Returns:
            True表示结构有效，False表示无效
        """
        if not self._get_modelscope_key():
            # 没有API时，本地简单验证
            return self._validate_optimization_structure(data)
        
        try:
            # 使用配置文件中的提示词
            prompt = STRUCTURE_VALIDATION_PROMPT.format(
                json_data=json.dumps(data, ensure_ascii=False, indent=2)
            )
            
            # 构建消息
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 调用API
            result = self._call_modelscope_api(
                model=config.VALIDATE_MODEL,
                messages=messages,
                temperature=0.1,
                max_tokens=500
            )
            
            if result and 'YES' in result.upper():
                print("[AI Service] 结构验证通过")
                return True
            else:
                print(f"[AI Service] 结构验证失败: {result}")
                return False
                
        except Exception as e:
            print(f"[AI Service] 结构验证异常: {e}")
            # 异常时回退到本地验证
            return self._validate_optimization_structure(data)
    
    def chat(self, message: str, history: list = None) -> str:
        """
        通用对话功能（纯文本）
        
        Args:
            message: 用户消息
            history: 历史对话列表，格式: [{"role": "user", "content": "..."}, ...]
            
        Returns:
            AI的回复
        """
        if not self._get_modelscope_key():
            return "抱歉，AI功能未配置。请联系管理员设置MODELSCOPE_API_KEY。"
        
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            messages.append({
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT
            })
            
            # 添加历史对话
            if history:
                messages.extend(history)
            
            # 添加当前消息
            messages.append({
                "role": "user",
                "content": message
            })
            
            # 调用API（使用优化模型进行对话）
            result = self._call_modelscope_api(
                model=config.OPTIMIZE_MODEL,  # 使用思考模型
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            if result:
                return result
            else:
                return "抱歉，我现在无法回答。请稍后再试。"
                
        except Exception as e:
            print(f"[AI Service] 对话异常: {e}")
            return "抱歉，处理您的请求时出现了问题。"
    
    def chat_with_image(self, message: str, image_path: str = None, history: list = None) -> str:
        """
        支持图片的对话功能（多模态）
        使用阿里云百炼的qwen-vl-plus模型
        
        Args:
            message: 用户消息文本
            image_path: 可选的图片路径
            history: 历史对话列表，格式: [{"role": "user/assistant", "content": "..."}, ...]
            
        Returns:
            AI的回复（Markdown格式）
        """
        dashscope_key = self._get_dashscope_key()
        if not dashscope_key:
            return "抱歉，AI功能未配置。请联系管理员设置DASHSCOPE_API_KEY。"
        
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统提示词
            messages.append({
                "role": "system",
                "content": CHAT_SYSTEM_PROMPT
            })
            
            # 添加历史对话（只添加文本部分，保持简洁）
            if history:
                for msg in history:
                    # 只保留role和content，移除image_url等额外字段
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # 构建当前用户消息
            if image_path and Path(image_path).exists():
                # 多模态输入：文本 + 图片
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                
                user_message = {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            else:
                # 纯文本输入
                user_message = {
                    "role": "user",
                    "content": message
                }
            
            messages.append(user_message)
            
            # 调用阿里云百炼API
            print(f"[AI Service] 调用阿里云百炼 {config.CHAT_MODEL} 进行对话")
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {dashscope_key}'
            }
            
            payload = {
                "model": config.CHAT_MODEL,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{config.DASHSCOPE_API_BASE}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code != 200:
                print(f"[AI Service] API返回错误: {response.status_code}")
                print(f"[AI Service] 错误详情: {response.text}")
                return "抱歉，调用AI服务时出现错误。请稍后再试。"
            
            result = response.json()
            
            # 提取返回内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                if content:
                    print(f"[AI Service] 对话成功，返回内容长度: {len(content)}")
                    return content
                else:
                    return "抱歉，AI没有返回有效内容。"
            else:
                print(f"[AI Service] 响应格式异常: {result}")
                return "抱歉，AI响应格式异常。"
                
        except requests.exceptions.Timeout:
            print(f"[AI Service] API调用超时")
            return "抱歉，请求超时。请稍后再试。"
        except Exception as e:
            print(f"[AI Service] 对话异常: {e}")
            return f"抱歉，处理您的请求时出现了问题：{str(e)}"
    
    # ==================== 辅助方法 ====================
    
    def _validate_optimization_structure(self, data: Dict) -> bool:
        """本地验证优化结果的结构"""
        # 必需的顶层字段
        required_fields = ['original_text', 'score', 'optimized_text', 'suggestions']
        
        # suggestions 必需的子字段
        required_suggestion_fields = [
            'topic_compliance',
            'spelling_errors',
            'grammar_errors',
            'word_optimization',
            'sentence_optimization',
            'structure_optimization'
        ]
        
        # 检查顶层字段
        for field in required_fields:
            if field not in data:
                print(f"[验证] 缺少字段: {field}")
                return False
        
        # 检查 score 结构
        score = data.get('score', {})
        if not isinstance(score, dict):
            print(f"[验证] score 不是字典类型")
            return False
        if 'level' not in score or 'points' not in score:
            print(f"[验证] score 缺少 level 或 points 字段")
            return False
        
        # 检查 suggestions 的子字段
        suggestions = data.get('suggestions', {})
        for field in required_suggestion_fields:
            if field not in suggestions:
                print(f"[验证] suggestions 缺少字段: {field}")
                return False
            if not isinstance(suggestions[field], list):
                print(f"[验证] suggestions.{field} 不是列表类型")
                return False
        
        return True
    
    def _get_placeholder_ocr_result(self) -> str:
        """获取占位符OCR结果"""
        return """Dear Sir or Madam,

I am writing to express my keen interest in the summer camp program. I believe this is an excellent opportunity for me to improve my English skills and learn about different cultures.

I am a 16-year-old high school student who is passionate about English learning. In my spare time, I enjoy reading English novels and watching English movies. I have also participated in several English speech contests and won some awards.

I would be grateful if you could provide me with more information about the program, including the schedule, accommodation, and fees.

I look forward to hearing from you soon.

Yours sincerely,
Li Hua"""
    
    def _get_placeholder_optimization(self) -> Dict:
        """获取占位符优化结果"""
        return {
            "original_text": """Dear Sir,

I want join your camp. I like English very much. Please tell me more information.

Thanks,
Li Hua""",
            "score": {
                "level": "第三档",
                "points": 6
            },
            "optimized_text": """Dear Sir or Madam,

I am writing to express my keen interest in your summer camp program. I believe this presents an excellent opportunity for me to enhance my English proficiency and gain exposure to diverse cultures.

As a passionate 16-year-old high school student, I have developed a strong enthusiasm for English learning. In my leisure time, I enjoy immersing myself in English literature and cinema. Additionally, I have actively participated in various English speech competitions, achieving notable recognition.

I would greatly appreciate it if you could provide me with comprehensive information regarding the program, including the schedule, accommodation arrangements, and associated fees.

I eagerly await your response.

Yours sincerely,
Li Hua""",
            "suggestions": {
                "topic_compliance": [
                    "基本完成写信任务，但格式不够规范（称呼过于简单），内容要点基本覆盖但不够充分"
                ],
                "spelling_errors": [
                    "无明显拼写错误"
                ],
                "grammar_errors": [
                    "want join → want to join (缺少不定式符号to)",
                    "tell me more information → provide me with more information (搭配不当)"
                ],
                "word_optimization": [
                    "want → would like to / be eager to (更正式)",
                    "like → have a passion for / be enthusiastic about (更学术)",
                    "tell → provide / inform (更恰当的书信用语)"
                ],
                "sentence_optimization": [
                    "原文句式过于简单，建议使用复合句增加表现力",
                    "可添加原因状语从句说明为何想参加",
                    "结尾应使用正式的期待回复表达"
                ],
                "structure_optimization": [
                    "称呼应使用'Dear Sir or Madam'（不知道具体姓名时）",
                    "应分段：开头段说明目的、主体段介绍背景、结尾段礼貌收尾",
                    "落款应改为'Yours sincerely,'并在下一行署名"
                ]
            }
        }
