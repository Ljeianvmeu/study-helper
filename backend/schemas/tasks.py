from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class DailyTask(BaseModel):
    id: int
    date: str
    task_name: str
    completed: bool = False

class TaskCreate(BaseModel):
    date: str
    task_name: str

class TaskUpdate(BaseModel):
    completed: bool

class StudyRecordCreate(BaseModel):
    date: str
    study_hours: int
    study_minutes: int
    completed_task_ids: List[int]

class StudyRecordUpdate(BaseModel):
    date: str
    study_hours: int
    study_minutes: int
    completed_task_ids: List[int]

class DailyTasksResponse(BaseModel):
    date: str
    study_hours: float
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    tasks: List[DailyTask]

class ChartDataPoint(BaseModel):
    date: str
    study_hours: float
    completion_rate: float

