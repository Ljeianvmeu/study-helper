from fastapi import APIRouter, HTTPException, Query
from schemas.scores import (
    ScoreCreate, ScoreUpdate, ScoreResponse, 
    ScoreListResponse, ScoreQueryParams
)
from services.excel_service import ScoreExcelService
from typing import Optional, List, Dict
from datetime import date

router = APIRouter()
score_service = ScoreExcelService()

# 试卷类型映射
PAPER_TYPES = {
    "数学": ["真题", "合工大超越卷", "张宇四套卷", "李林四套卷", "李艳芳三套卷", "其他"],
    "专业课": ["真题", "模拟题", "其他"],
    "英语": ["真题", "其他"]
}

@router.get("/paper-types")
def get_paper_types(subject: str):
    """获取指定科目的试卷类型列表"""
    if subject not in PAPER_TYPES:
        raise HTTPException(status_code=400, detail="无效的科目")
    return {"paper_types": PAPER_TYPES[subject]}

@router.post("/scores", response_model=dict)
def create_score(score: ScoreCreate):
    """添加新的分数记录"""
    try:
        # 验证试卷类型
        if score.paper_type not in PAPER_TYPES[score.subject]:
            raise HTTPException(
                status_code=400, 
                detail=f"试卷类型 '{score.paper_type}' 不适用于科目 '{score.subject}'"
            )
        
        score_id = score_service.add_score(
            subject=score.subject,
            year=score.year,
            paper_type=score.paper_type,
            score=score.score,
            input_date=score.input_date
        )
        
        return {
            "message": "分数记录添加成功",
            "id": score_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scores", response_model=ScoreListResponse)
def get_scores(
    subject: Optional[str] = None,
    paper_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """获取分数列表，支持筛选和分页"""
    try:
        records, total = score_service.get_scores(
            subject=subject,
            paper_type=paper_type,
            page=page,
            page_size=page_size
        )
        
        if not records:
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "data": []
            }
        
        # 转换数据格式
        data = [
            {
                "id": int(r['ID']),
                "subject": r['科目'],
                "year": int(r['年份']),
                "paper_type": r['试卷类型'],
                "score": float(r['分数']),
                "input_date": r['录入日期'].date() if hasattr(r['录入日期'], 'date') else r['录入日期']
            }
            for r in records
        ]
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/scores/{score_id}")
def update_score(score_id: int, score: ScoreUpdate):
    """更新分数记录"""
    try:
        update_data = score.dict(exclude_unset=True)
        if update_data:
            # 转换日期格式
            if 'input_date' in update_data:
                update_data['录入日期'] = update_data.pop('input_date').strftime('%Y-%m-%d')
            if 'subject' in update_data:
                update_data['科目'] = update_data.pop('subject')
            if 'year' in update_data:
                update_data['年份'] = update_data.pop('year')
            if 'paper_type' in update_data:
                update_data['试卷类型'] = update_data.pop('paper_type')
            if 'score' in update_data:
                update_data['分数'] = update_data.pop('score')
            
            score_service.update_row(score_id, update_data)
        return {"message": "分数记录更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/scores/{score_id}")
def delete_score(score_id: int):
    """删除分数记录"""
    try:
        score_service.delete_row(score_id)
        return {"message": "分数记录删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scores/chart-data")
def get_chart_data(
    subject: str,
    paper_type: Optional[str] = None
):
    """获取图表数据"""
    try:
        data = score_service.get_chart_data(subject, paper_type)
        
        if not data:
            return {
                "message": "未查询到相关数据",
                "data": [],
                "dates": [],
                "scores": []
            }
        
        # 格式化数据供ECharts使用
        dates = [d['录入日期'].strftime('%Y-%m-%d') for d in data]
        scores = [float(d['分数']) for d in data]
        
        return {
            "dates": dates,
            "scores": scores,
            "subject": subject
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
