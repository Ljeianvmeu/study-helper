"""
配置文件
"""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# 加载.env文件（开发环境使用）
load_dotenv()

# 全局变量（延迟初始化）
_DATA_ROOT = None
_API_CONFIG_FILE = None

# 获取程序运行的基础目录
def get_app_base_dir() -> Path:
    """
    获取应用程序的基础目录
    - 开发环境：返回 backend 目录
    - 打包环境：返回 exe 文件所在目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        exe_path = Path(sys.executable).parent
        # 打印调试信息
        print(f"[Config] Executable path: {sys.executable}")
        print(f"[Config] Exe parent: {exe_path}")
        return exe_path
    else:
        # 开发环境
        return Path(__file__).parent

# 获取数据存储根目录
def get_data_root_dir() -> Path:
    """
    获取数据存储根目录
    优先使用环境变量指定的路径，否则使用默认位置
    """
    global _DATA_ROOT
    
    # 如果已经初始化过，直接返回
    if _DATA_ROOT is not None:
        return _DATA_ROOT
    
    # 1. 最优先：检查环境变量（由 Electron 主进程设置）
    data_root_env = os.getenv('STUDY_HELPER_DATA_ROOT')
    if data_root_env:
        print(f"[Config] Using data root from env: {data_root_env}")
        _DATA_ROOT = Path(data_root_env)
        _DATA_ROOT.mkdir(parents=True, exist_ok=True)
        return _DATA_ROOT
    
    # 2. 获取基础目录
    base_dir = get_app_base_dir()
    print(f"[Config] Base dir: {base_dir}")
    
    # 3. 如果是打包环境
    if getattr(sys, 'frozen', False):
        base_str = str(base_dir)
        print(f"[Config] Frozen mode, checking path: {base_str}")
        
        # 检查是否在 Electron 的 resources/backend 目录下
        if 'resources' in base_str and 'backend' in base_str:
            # 路径: 安装目录/resources/backend/
            # 向上两级: 安装目录/resources/ -> 安装目录/
            app_root = base_dir.parent.parent
            print(f"[Config] Detected Electron app, root: {app_root}")
            _DATA_ROOT = app_root / "study-helper"
        else:
            # 独立运行的打包 exe
            _DATA_ROOT = base_dir / "study-helper"
    else:
        # 开发环境
        _DATA_ROOT = base_dir / "study-helper"
    
    print(f"[Config] Final data root: {_DATA_ROOT}")
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return _DATA_ROOT

# 获取API配置文件路径
def get_api_config_file() -> Path:
    """获取API配置文件路径"""
    global _API_CONFIG_FILE
    if _API_CONFIG_FILE is None:
        _API_CONFIG_FILE = get_data_root_dir() / "api_config.json"
    return _API_CONFIG_FILE

# 从配置文件加载API密钥
def load_api_keys():
    """从配置文件加载API密钥"""
    api_file = get_api_config_file()
    if api_file.exists():
        with open(api_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('MODELSCOPE_API_KEY', ''), config.get('DASHSCOPE_API_KEY', '')
    # 如果配置文件不存在，尝试从环境变量读取（开发环境）
    return os.getenv("MODELSCOPE_API_KEY", ""), os.getenv("DASHSCOPE_API_KEY", "")

# 保存API密钥到配置文件
def save_api_keys(modelscope_key: str, dashscope_key: str):
    """保存API密钥到配置文件"""
    config = {
        'MODELSCOPE_API_KEY': modelscope_key,
        'DASHSCOPE_API_KEY': dashscope_key
    }
    api_file = get_api_config_file()
    with open(api_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 检查API配置是否存在
def check_api_config_exists() -> bool:
    """检查API配置文件是否存在"""
    return get_api_config_file().exists()

# 加载API密钥（模块级变量）
_MODELSCOPE_API_KEY = None
_DASHSCOPE_API_KEY = None

def get_api_keys():
    """获取API密钥（动态读取）"""
    global _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY
    
    # 如果还没加载过，加载一次
    if _MODELSCOPE_API_KEY is None and _DASHSCOPE_API_KEY is None:
        _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY = load_api_keys()
    
    return _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY

def reload_api_keys():
    """重新加载API密钥"""
    global _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY
    _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY = load_api_keys()
    return _MODELSCOPE_API_KEY, _DASHSCOPE_API_KEY

# 初始加载
MODELSCOPE_API_KEY, DASHSCOPE_API_KEY = get_api_keys()

# ModelScope API基础URL（经过测试验证的端点）
MODELSCOPE_API_BASE = "https://api-inference.modelscope.cn/v1/chat/completions"

# 阿里云百炼 DashScope API配置（用于Chat功能）
DASHSCOPE_API_BASE = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 模型配置（使用ModelScope平台的模型）
# 使用 Qwen3-VL-30B-A3B-Thinking - ModelScope API 推理服务支持的多模态思考模型
VISION_MODEL = "Qwen/Qwen3-VL-30B-A3B-Thinking"  # 主力：多模态思考模型（视觉+思考）
OCR_MODEL = "Qwen/Qwen3-VL-30B-A3B-Instruct"  # 备用：纯视觉理解模型
OPTIMIZE_MODEL = "Qwen/Qwen3-30B-A3B-Thinking-2507"  # 备用：纯文本思考模型
VALIDATE_MODEL = "Qwen/Qwen3-30B-A3B-Instruct-2507"  # 结构验证模型

# Chat功能使用的模型（阿里云百炼）
CHAT_MODEL = "qwen-vl-plus"  # 支持多模态（文本+图片）的对话模型

# 文件路径配置（使用函数确保正确初始化）
def _init_dirs():
    """初始化所有目录"""
    root = get_data_root_dir()
    
    data_dir = root / "data"
    temp_dir = root / "temp"
    output_dir = root / "output"
    topics_dir = data_dir / "topics"
    chat_history_dir = output_dir / "chat_history"
    
    # 确保目录存在
    data_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    topics_dir.mkdir(parents=True, exist_ok=True)
    chat_history_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir, temp_dir, output_dir, topics_dir, chat_history_dir

# 初始化目录
DATA_DIR, TEMP_DIR, OUTPUT_DIR, TOPICS_DIR, CHAT_HISTORY_DIR = _init_dirs()

# 兼容性：保持旧的变量名
BASE_DIR = get_app_base_dir()
UPLOADS_DIR = TEMP_DIR

