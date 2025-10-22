from pydantic import BaseModel, Field, validator
from datetime import date
from typing import Optional, Literal

class ScoreCreate(BaseModel):
    subject: Literal["数学", "专业课", "英语"]
    year: int
    paper_type: str
    score: float
    input_date: date
    
    @validator('year')
    def validate_year(cls, v):
        if v < 2000 or v > 2100:
            raise ValueError('年份必须在2000-2100之间')
        return v
    
    @validator('score')
    def validate_score(cls, v, values):
        subject = values.get('subject')
        if subject in ["数学", "专业课"] and (v < 0 or v > 150):
            raise ValueError(f'{subject}分数必须在0-150之间')
        elif subject == "英语" and (v < 0 or v > 100):
            raise ValueError('英语分数必须在0-100之间')
        return v

class ScoreUpdate(BaseModel):
    subject: Optional[Literal["数学", "专业课", "英语"]]
    year: Optional[int]
    paper_type: Optional[str]
    score: Optional[float]
    input_date: Optional[date]

class ScoreResponse(BaseModel):
    id: int
    subject: str
    year: int
    paper_type: str
    score: float
    input_date: date

class ScoreListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list

class ScoreQueryParams(BaseModel):
    subject: Optional[str] = None
    paper_type: Optional[str] = None
    page: int = 1
    page_size: int = 10
