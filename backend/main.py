# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api import chat as chat_api, scores as scores_api, essays as essays_api, tasks as tasks_api, system as system_api
from pathlib import Path
import config
import shutil
import atexit

# --- 应用创建 ---
app = FastAPI(
    title="Study Helper API",
    description="个人学习助手后端API",
    version="0.1.0"
)

# --- CORS 中间件配置 ---
# 2. 定义允许的源列表。在开发环境中，我们允许来自 Vite 前端的请求。
origins = [
    "http://localhost:5173",
]

# 3. 将 CORS 中间件添加到应用中
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有请求头
)

# --- 路由包含 ---
app.include_router(chat_api.router, prefix="/api/v1", tags=["Chat"])
app.include_router(scores_api.router, prefix="/api/v1", tags=["Scores"])
app.include_router(essays_api.router, prefix="/api/v1", tags=["Essays"])
app.include_router(tasks_api.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(system_api.router, prefix="/api/v1", tags=["System"])

# --- 静态文件服务 ---
# 挂载 data 目录，使前端可以直接访问图片等静态资源
data_path = config.DATA_DIR
if data_path.exists():
    app.mount("/data", StaticFiles(directory=str(data_path)), name="data")

# --- 程序关闭时的清理逻辑 ---
def cleanup_on_exit():
    """程序关闭时清理临时文件"""
    try:
        if config.TEMP_DIR.exists():
            shutil.rmtree(config.TEMP_DIR)
            print("临时文件已清理")
    except Exception as e:
        print(f"清理临时文件时出错: {e}")

# 注册退出时的清理函数
atexit.register(cleanup_on_exit)

# --- 根路径 ---
@app.get("/")
def read_root():
    return {"message": "欢迎使用 Study Helper API"}

# --- 程序入口 ---
if __name__ == "__main__":
    import uvicorn
    import sys
    import logging
    
    # 检查是否为打包环境
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # 打包环境：使用文件日志
        import os
        from pathlib import Path
        
        # 创建日志文件
        log_file = Path(os.getenv('STUDY_HELPER_DATA_ROOT', '.')) / 'backend.log'
        
        # 配置基础日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("="*50)
        logger.info("Study Helper Backend Starting...")
        logger.info(f"Data root: {os.getenv('STUDY_HELPER_DATA_ROOT', 'Not Set')}")
        logger.info("="*50)
        
        # 启动服务器（不使用 uvicorn 的日志配置）
        try:
            uvicorn.run(
                app, 
                host="127.0.0.1", 
                port=8000,
                log_config=None,
                access_log=False
            )
        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            raise
    else:
        # 开发环境：使用默认配置
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")