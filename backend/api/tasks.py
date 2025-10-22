from fastapi import APIRouter, HTTPException, Query
from schemas.tasks import (
    StudyRecordCreate, 
    StudyRecordUpdate, 
    DailyTasksResponse,
    DailyTask,
    TaskCreate,
    ChartDataPoint
)
from services.excel_service import DailyTaskService, StudyRecordService
from datetime import datetime, timedelta
from typing import List

router = APIRouter()
task_service = DailyTaskService()
record_service = StudyRecordService()

@router.get("/tasks/by-date", response_model=DailyTasksResponse)
def get_tasks_by_date(date: str = Query(..., description="日期，格式: YYYY-MM-DD")):
    """
    获取指定日期的任务和学习记录
    如果该日期还没有任务，自动初始化默认任务
    """
    try:
        # 初始化该日期的默认任务（如果没有）
        task_service.init_default_tasks_for_date(date)
        
        # 获取该日期的所有任务
        tasks_data = task_service.get_tasks_by_date(date)
        
        # 获取学习记录
        study_record = record_service.get_record_by_date(date)
        study_hours = float(study_record.get('学习时长(小时)', 0)) if study_record else 0.0
        
        # 计算完成率
        total_tasks = len(tasks_data)
        completed_tasks = len([t for t in tasks_data if t.get('是否完成', False)])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        # 构建任务列表
        tasks = [
            DailyTask(
                id=int(task['ID']),
                date=task['日期'],
                task_name=task['任务名称'],
                completed=bool(task.get('是否完成', False))
            )
            for task in tasks_data
        ]
        
        return {
            "date": date,
            "study_hours": study_hours,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate,
            "tasks": tasks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务失败: {str(e)}")

@router.post("/tasks/add")
def add_task(task: TaskCreate):
    """为指定日期添加新任务"""
    try:
        task_id = task_service.add_task(
            date_str=task.date,
            task_name=task.task_name,
            completed=False
        )
        return {
            "message": "任务添加成功",
            "task_id": task_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加任务失败: {str(e)}")

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """删除任务"""
    try:
        task_service.delete_task(task_id)
        return {"message": "任务删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")

@router.post("/tasks/save")
def save_study_record(record: StudyRecordCreate):
    """保存学习记录和任务完成状态"""
    try:
        # 将小时和分钟转换为小时（浮点数）
        total_hours = record.study_hours + record.study_minutes / 60.0
        
        # 更新任务完成状态
        task_service.update_tasks_for_date(record.date, record.completed_task_ids)
        
        # 保存学习时长记录
        record_service.save_record(
            date_str=record.date,
            study_hours=total_hours
        )
        
        # 计算完成率
        tasks_data = task_service.get_tasks_by_date(record.date)
        total_tasks = len(tasks_data)
        completed_tasks = len(record.completed_task_ids)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "message": "学习记录保存成功",
            "study_hours": total_hours,
            "completion_rate": completion_rate
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")

@router.put("/tasks/record")
def update_study_record(record: StudyRecordUpdate):
    """更新学习记录和任务完成状态"""
    try:
        # 检查记录是否存在
        existing_record = record_service.get_record_by_date(record.date)
        if not existing_record:
            raise HTTPException(status_code=404, detail=f"{record.date} 没有学习记录")
        
        # 将小时和分钟转换为小时（浮点数）
        total_hours = record.study_hours + record.study_minutes / 60.0
        
        # 更新任务完成状态
        task_service.update_tasks_for_date(record.date, record.completed_task_ids)
        
        # 更新学习时长记录
        record_service.save_record(
            date_str=record.date,
            study_hours=total_hours
        )
        
        # 计算完成率
        tasks_data = task_service.get_tasks_by_date(record.date)
        total_tasks = len(tasks_data)
        completed_tasks = len(record.completed_task_ids)
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        return {
            "message": "学习记录更新成功",
            "study_hours": total_hours,
            "completion_rate": completion_rate
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@router.get("/tasks/chart-data")
def get_chart_data(view: str = Query("week", regex="^(week|month|all)$")):
    """
    获取图表数据
    view: week(最近7天) | month(最近30天) | all(全部)
    """
    try:
        today = datetime.now().date()
        
        if view == "week":
            start_date = today - timedelta(days=6)
        elif view == "month":
            start_date = today - timedelta(days=29)
        else:  # all
            start_date = datetime(2000, 1, 1).date()
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = today.strftime('%Y-%m-%d')
        
        # 获取学习时长记录
        study_records = record_service.get_records_by_range(start_str, end_str)
        
        if not study_records:
            return {"data": []}
        
        # 转换数据格式并计算完成率
        chart_data = []
        for record in study_records:
            date_str = record['日期'].strftime('%Y-%m-%d') if hasattr(record['日期'], 'strftime') else str(record['日期'])
            
            # 获取该日期的任务完成情况
            tasks_data = task_service.get_tasks_by_date(date_str)
            total_tasks = len(tasks_data)
            completed_tasks = len([t for t in tasks_data if t.get('是否完成', False)])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
            
            chart_data.append({
                "date": date_str,
                "study_hours": float(record.get('学习时长(小时)', 0)),
                "completion_rate": completion_rate
            })
        
        return {"data": chart_data}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")
