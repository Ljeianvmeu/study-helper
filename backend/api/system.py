"""
系统配置API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import shutil
from pathlib import Path
import config

router = APIRouter()


class APIKeysRequest(BaseModel):
    modelscope_api_key: str
    dashscope_api_key: str


class APIKeysResponse(BaseModel):
    success: bool
    message: str


class SystemStatusResponse(BaseModel):
    api_configured: bool
    daily_tasks_exists: bool


@router.get("/system/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    获取系统配置状态
    """
    api_configured = config.check_api_config_exists()
    daily_tasks_file = config.DATA_DIR / "daily_tasks.xlsx"
    daily_tasks_exists = daily_tasks_file.exists()
    
    return SystemStatusResponse(
        api_configured=api_configured,
        daily_tasks_exists=daily_tasks_exists
    )


@router.post("/system/api-keys", response_model=APIKeysResponse)
async def save_api_keys(request: APIKeysRequest):
    """
    保存API密钥配置
    """
    try:
        config.save_api_keys(
            request.modelscope_api_key,
            request.dashscope_api_key
        )
        
        # 重新加载API密钥到全局变量
        config.MODELSCOPE_API_KEY, config.DASHSCOPE_API_KEY = config.reload_api_keys()
        
        return APIKeysResponse(
            success=True,
            message="API密钥保存成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存API密钥失败: {str(e)}")


@router.post("/system/upload-daily-tasks")
async def upload_daily_tasks(file: UploadFile = File(...)):
    """
    上传 daily_tasks.xlsx 文件
    """
    try:
        # 检查文件扩展名
        if not file.filename.endswith('.xlsx'):
            raise HTTPException(status_code=400, detail="只能上传 .xlsx 格式的文件")
        
        # 检查文件是否已存在
        daily_tasks_file = config.DATA_DIR / "daily_tasks.xlsx"
        if daily_tasks_file.exists():
            raise HTTPException(status_code=400, detail="daily_tasks.xlsx 文件已存在")
        
        # 保存文件
        with open(daily_tasks_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "message": "daily_tasks.xlsx 上传成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传文件失败: {str(e)}")


@router.delete("/system/cleanup-temp")
async def cleanup_temp():
    """
    清理临时文件夹
    """
    try:
        temp_dir = config.TEMP_DIR
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)
        
        return {
            "success": True,
            "message": "临时文件清理成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清理临时文件失败: {str(e)}")

