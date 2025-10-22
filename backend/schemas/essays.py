from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class EssayScore(BaseModel):
    """作文评分"""
    level: str  # 档位，如"第三档"
    points: int  # 具体分数

class EssayAnalysisResponse(BaseModel):
    """作文分析响应"""
    topic: str  # 题目（可能是文本描述或图片路径提示）
    topic_image_path: Optional[str] = None  # 题目图片路径
    reference_essay: str  # 参考范文
    original_text: str  # 识别出的学生原文
    score: EssayScore  # 评分信息
    optimized_text: str  # 优化后的作文
    suggestions: Dict[str, Any]  # 建议

class EssaySuggestions(BaseModel):
    """作文建议"""
    topic_compliance: List[str]  # 主题贴合度
    spelling_errors: List[str]  # 拼写错误
    grammar_errors: List[str]  # 语法错误
    word_optimization: List[str]  # 词汇优化
    sentence_optimization: List[str]  # 句式优化
    structure_optimization: List[str]  # 结构优化

class TopicInfo(BaseModel):
    """题目信息"""
    year: int
    essay_type: str  # '小作文' 或 '大作文'
    topic_image_path: str  # 题目图片路径
    reference_essay: str  # 参考范文

