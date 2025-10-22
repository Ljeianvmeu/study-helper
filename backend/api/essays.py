from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import FileResponse
from schemas.essays import EssayAnalysisResponse
from services.excel_service import EssayTopicService
from services.ai_service import AIService
from services.image_service import ImageService
from config import TOPICS_DIR
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any

router = APIRouter()
topic_service = EssayTopicService()
ai_service = AIService()
image_service = ImageService()

@router.get("/essays/topics")
def get_topics():
    """获取所有可用的年份和作文类型"""
    try:
        years = topic_service.get_all_years()
        essay_types = topic_service.get_essay_types()
        return {"years": years, "essay_types": essay_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/essays/topics")
async def add_topic(
    year: int = Form(...),
    essay_type: str = Form(...),
    topic_image: UploadFile = File(...),
    reference: str = Form(...)
):
    """添加作文题目"""
    try:
        # 保存题目图片
        image_content = await topic_image.read()
        # 将中文作文类型转换为英文，避免文件名中出现中文
        essay_type_short = "small" if essay_type == "小作文" else "large"
        filename = f"topic_{year}_{essay_type_short}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        
        # 保存到topics目录
        file_path = TOPICS_DIR / filename
        with open(file_path, 'wb') as f:
            f.write(image_content)
        
        # 存储相对路径
        relative_path = f"data/topics/{filename}"
        
        # 添加到数据库
        topic_service.add_topic(year, essay_type, relative_path, reference)
        
        return {"message": "题目添加成功", "image_path": relative_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/essays/topics/{year}/{essay_type}")
def get_topic_detail(year: int, essay_type: str):
    """获取特定年份和类型的题目详情"""
    try:
        topic_data = topic_service.get_topic_by_year_and_type(year, essay_type)
        if not topic_data:
            raise HTTPException(status_code=404, detail="未找到题目")
        return topic_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/essays/topics/image/{year}/{essay_type}")
def get_topic_image(year: int, essay_type: str):
    """获取题目图片"""
    try:
        topic_data = topic_service.get_topic_by_year_and_type(year, essay_type)
        if not topic_data:
            raise HTTPException(status_code=404, detail="未找到题目")
        
        image_path = Path(topic_data['题目图片路径'])
        if not image_path.exists():
            raise HTTPException(status_code=404, detail="题目图片不存在")
        
        return FileResponse(image_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/essays/topics/{year}/{essay_type}")
def delete_topic(year: int, essay_type: str):
    """删除作文题目"""
    try:
        # 获取题目数据以删除图片
        topic_data = topic_service.get_topic_by_year_and_type(year, essay_type)
        if topic_data:
            # 删除图片文件
            image_path = Path(topic_data['题目图片路径'])
            if image_path.exists():
                image_path.unlink()
        
        # 从数据库删除
        topic_service.delete_topic(year, essay_type)
        
        return {"message": "题目删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/essays/ocr")
async def ocr_essay(
    year: int = Form(...),
    essay_type: str = Form(...),
    image: UploadFile = File(...)
):
    """
    第一步：OCR识别手写作文
    返回识别出的文字
    """
    try:
        # 1. 查找题目和范文（用于返回上下文信息）
        topic_data = topic_service.get_topic_by_year_and_type(year, essay_type)
        if not topic_data:
            raise HTTPException(status_code=404, detail=f"未找到{year}年{essay_type}的作文题目")
        
        # 2. 保存上传的图片
        image_content = await image.read()
        essay_type_short = "small" if essay_type == "小作文" else "large"
        filename = f"essay_{year}_{essay_type_short}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        image_path = image_service.save_upload_file(image_content, filename)
        
        # 3. 验证图片
        if not image_service.validate_image(image_path):
            image_service.cleanup_file(image_path)
            raise HTTPException(status_code=400, detail="无效的图片文件")
        
        # 4. 使用AI进行OCR识别
        print(f"[API] 开始OCR识别作文图片")
        original_text = ai_service.image_to_text(image_path)
        
        # 5. 返回识别结果和必要的上下文信息
        return {
            "original_text": original_text,
            "essay_image_path": image_path,  # 保存路径供后续优化使用
            "topic": f"{year}年{essay_type}",
            "topic_image_path": topic_data.get('题目图片路径', ''),
            "reference_essay": topic_data['参考范文']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR识别失败: {str(e)}")


@router.post("/essays/analyze", response_model=EssayAnalysisResponse)
async def analyze_essay(request_data: Dict[str, Any] = Body(...)):
    """
    第二步：优化作文
    接收OCR识别的文字，结合题目图片和范文进行优化
    """
    try:
        # 从请求中提取数据
        year = request_data.get('year')
        essay_type = request_data.get('essay_type')
        original_text = request_data.get('original_text')
        topic_image_path = request_data.get('topic_image_path')
        reference_essay = request_data.get('reference_essay')
        
        if not all([year, essay_type, original_text, reference_essay]):
            raise HTTPException(status_code=400, detail="缺少必需参数")
        
        # 使用optimize_essay方法（带题目图片的优化）
        print(f"[API] 使用文字版原文 + 题目图片进行优化")
        optimization_result = ai_service.optimize_essay(
            topic_image_path=topic_image_path,
            reference=reference_essay,
            original=original_text,
            essay_type=essay_type
        )
        
        # 验证结构
        is_valid = ai_service.validate_structure(optimization_result)
        if not is_valid:
            print("[API] [WARNING] 返回结构验证失败，但继续返回数据")
        
        # 确保原文被包含在结果中
        if 'original_text' not in optimization_result:
            optimization_result['original_text'] = original_text
        
        # 提取评分信息
        score_info = optimization_result.get('score', {'level': '未评分', 'points': 0})
        
        # 返回完整结果
        return {
            "topic": f"{year}年{essay_type}",
            "topic_image_path": topic_image_path,
            "reference_essay": reference_essay,
            "original_text": optimization_result.get('original_text', original_text),
            "score": score_info,
            "optimized_text": optimization_result.get('optimized_text', ''),
            "suggestions": optimization_result.get('suggestions', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")

@router.post("/essays/save")
def save_analysis(request_data: Dict[str, Any] = Body(...)):
    """
    保存分析结果为markdown文件
    """
    try:
        year = request_data.get('year')
        data = request_data.get('data')
        # 创建输出目录（统一到 data root 下的 study-helper/output/essays）
        from config import OUTPUT_DIR
        output_dir = OUTPUT_DIR / "essays"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"essay_analysis_{year}_{timestamp}.md"
        file_path = output_dir / filename
        
        # 获取打分信息
        score = data.get('score', {})
        score_text = ""
        if score:
            score_text = f"\n**评分**: {score.get('points', 0)}分 ({score.get('level', '未评分')})\n"
        
        # 生成markdown内容
        md_content = f"""# 英语作文分析报告

**年份**: {year}
**作文类型**: {data.get('essay_type', '')}
{score_text}**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📝 题目

{data.get('topic', '')}

---

## 📚 参考范文

```
{data.get('reference_essay', '')}
```

---

## 📊 作文对比

### 原文

```
{data.get('original_text', '')}
```

### 优化后

```
{data.get('optimized_text', '')}
```

---

## 💡 修改建议

### 1. 题意符合度

"""
        
        # 兼容 topic_compliance（新）和 topic_relevance（旧）
        suggestions = data.get('suggestions', {})
        topic_content = suggestions.get('topic_compliance') or suggestions.get('topic_relevance', [])
        if isinstance(topic_content, list) and topic_content:
            for item in topic_content:
                md_content += f"- {item}\n"
        elif isinstance(topic_content, str) and topic_content:
            md_content += f"{topic_content}\n"
        else:
            md_content += "无建议\n"
        
        md_content += "\n### 2. 拼写错误\n\n"
        
        spelling_errors = suggestions.get('spelling_errors', [])
        if spelling_errors:
            for error in spelling_errors:
                md_content += f"- {error}\n"
        else:
            md_content += "无拼写错误\n"
        
        md_content += "\n### 3. 语法错误\n\n"
        
        grammar_errors = suggestions.get('grammar_errors', [])
        if grammar_errors:
            for error in grammar_errors:
                md_content += f"- {error}\n"
        else:
            md_content += "无语法错误\n"
        
        md_content += "\n### 4. 单词优化\n\n"
        
        word_opts = suggestions.get('word_optimization', [])
        if word_opts:
            for opt in word_opts:
                md_content += f"- {opt}\n"
        else:
            md_content += "无需优化\n"
        
        md_content += "\n### 5. 句式优化\n\n"
        
        sentence_opts = suggestions.get('sentence_optimization', [])
        if sentence_opts:
            for opt in sentence_opts:
                md_content += f"- {opt}\n"
        else:
            md_content += "无需优化\n"
        
        md_content += "\n### 6. 结构优化\n\n"
        
        structure_opt = suggestions.get('structure_optimization', [])
        if isinstance(structure_opt, list) and structure_opt:
            for opt in structure_opt:
                md_content += f"- {opt}\n"
        elif isinstance(structure_opt, str) and structure_opt:
            md_content += f"{structure_opt}\n"
        else:
            md_content += "无需优化\n"
        
        md_content += "\n\n---\n\n*该报告由Study Helper自动生成*\n"
        
        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return {
            "message": "分析报告已保存",
            "file_path": str(file_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

