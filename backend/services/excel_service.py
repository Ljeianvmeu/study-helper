from pathlib import Path
from datetime import date, datetime
from typing import List, Dict, Optional
import pandas as pd

class ExcelService:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """确保Excel文件存在，如果不存在则创建"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            # 创建一个空的DataFrame并保存为Excel
            df = pd.DataFrame()
            df.to_excel(self.file_path, index=False)
    
    def read_all(self) -> pd.DataFrame:
        """读取所有数据"""
        try:
            df = pd.read_excel(self.file_path)
            return df
        except Exception as e:
            print(f"读取Excel失败: {e}")
            return pd.DataFrame()
    
    def append_row(self, data: Dict):
        """追加一行数据"""
        # 使用pandas追加，保证列顺序一致
        df = self.read_all()
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(self.file_path, index=False)
    
    def update_row(self, row_id: int, data: Dict):
        """更新指定行"""
        df = self.read_all()
        for key, value in data.items():
            if key in df.columns:
                df.at[row_id - 1, key] = value
        df.to_excel(self.file_path, index=False)
    
    def delete_row(self, row_id: int):
        """删除指定行"""
        df = self.read_all()
        df = df.drop(row_id - 1)
        df.to_excel(self.file_path, index=False)


class ScoreExcelService(ExcelService):
    def __init__(self):
        from config import DATA_DIR
        super().__init__(str(DATA_DIR / "scores.xlsx"))
        self._init_headers()
    
    def _init_headers(self):
        """初始化表头"""
        df = self.read_all()
        # 如果文件为空或没有正确的列，初始化表头
        if df.empty or 'ID' not in df.columns:
            df = pd.DataFrame(columns=['ID', '科目', '年份', '试卷类型', '分数', '录入日期'])
            df.to_excel(self.file_path, index=False)
    
    def get_next_id(self) -> int:
        """获取下一个ID"""
        df = self.read_all()
        if df.empty or 'ID' not in df.columns:
            return 1
        if len(df) == 0:
            return 1
        # 确保ID列是数值类型
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        max_id = df['ID'].max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    
    def add_score(self, subject: str, year: int, paper_type: str, 
                  score: float, input_date: date) -> int:
        """添加分数记录"""
        score_id = self.get_next_id()
        data = {
            'ID': score_id,
            '科目': subject,
            '年份': year,
            '试卷类型': paper_type,
            '分数': score,
            '录入日期': input_date.strftime('%Y-%m-%d')
        }
        self.append_row(data)
        return score_id
    
    def get_scores(self, subject: Optional[str] = None, 
                   paper_type: Optional[str] = None,
                   page: int = 1, page_size: int = 10) -> tuple:
        """获取分数列表，支持筛选和分页"""
        df = self.read_all()
        
        if df.empty:
            return [], 0
        
        # 筛选
        if subject:
            df = df[df['科目'] == subject]
        if paper_type:
            df = df[df['试卷类型'] == paper_type]
        
        # 按日期排序（新到旧）
        df['录入日期'] = pd.to_datetime(df['录入日期'])
        df = df.sort_values('录入日期', ascending=False)
        
        total = len(df)
        
        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx]
        
        # 转换为字典列表
        records = df_page.to_dict('records')
        return records, total
    
    def get_chart_data(self, subject: str, 
                       paper_type: Optional[str] = None) -> List[Dict]:
        """获取图表数据"""
        df = self.read_all()
        
        if df.empty:
            return []
        
        # 筛选
        df = df[df['科目'] == subject]
        if paper_type:
            df = df[df['试卷类型'] == paper_type]
        
        # 按日期排序（旧到新，用于图表）
        df['录入日期'] = pd.to_datetime(df['录入日期'])
        df = df.sort_values('录入日期', ascending=True)
        
        # 返回数据
        return df[['录入日期', '分数']].to_dict('records')


class EssayTopicService(ExcelService):
    """英语作文题库服务"""
    def __init__(self):
        from config import DATA_DIR
        super().__init__(str(DATA_DIR / "essays.xlsx"))
        self._init_headers()
    
    def _init_headers(self):
        """初始化表头"""
        df = self.read_all()
        if df.empty or '年份' not in df.columns:
            df = pd.DataFrame(columns=['年份', '作文类型', '题目图片路径', '参考范文'])
            df.to_excel(self.file_path, index=False)
    
    def add_topic(self, year: int, essay_type: str, topic_image_path: str, reference: str):
        """
        添加作文题目
        
        Args:
            year: 年份
            essay_type: 作文类型（'小作文' 或 '大作文'）
            topic_image_path: 题目图片路径
            reference: 参考范文
        """
        data = {
            '年份': year,
            '作文类型': essay_type,
            '题目图片路径': topic_image_path,
            '参考范文': reference
        }
        self.append_row(data)
    
    def update_topic(self, year: int, essay_type: str, topic_image_path: str = None, reference: str = None):
        """
        更新作文题目
        
        Args:
            year: 年份
            essay_type: 作文类型
            topic_image_path: 题目图片路径（可选）
            reference: 参考范文（可选）
        """
        df = self.read_all()
        mask = (df['年份'] == year) & (df['作文类型'] == essay_type)
        
        if topic_image_path:
            df.loc[mask, '题目图片路径'] = topic_image_path
        if reference:
            df.loc[mask, '参考范文'] = reference
        
        df.to_excel(self.file_path, index=False)
    
    def delete_topic(self, year: int, essay_type: str):
        """
        删除作文题目
        
        Args:
            year: 年份
            essay_type: 作文类型
        """
        df = self.read_all()
        df = df[~((df['年份'] == year) & (df['作文类型'] == essay_type))]
        df.to_excel(self.file_path, index=False)
    
    def get_topic_by_year(self, year: int) -> Optional[Dict]:
        """根据年份获取题目和范文（兼容旧接口，默认返回小作文）"""
        return self.get_topic_by_year_and_type(year, '小作文')
    
    def get_topic_by_year_and_type(self, year: int, essay_type: str) -> Optional[Dict]:
        """
        根据年份和作文类型获取题目和范文
        
        Args:
            year: 年份
            essay_type: 作文类型（'小作文' 或 '大作文'）
            
        Returns:
            包含题目和参考范文的字典，如果未找到返回None
        """
        df = self.read_all()
        if df.empty:
            return None
        
        # 同时匹配年份和作文类型
        result = df[(df['年份'] == year) & (df['作文类型'] == essay_type)]
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()
    
    def get_all_years(self) -> List[int]:
        """获取所有可用的年份"""
        df = self.read_all()
        if df.empty:
            return []
        return sorted(df['年份'].unique().tolist(), reverse=True)
    
    def get_essay_types(self) -> List[str]:
        """获取所有作文类型"""
        return ['小作文', '大作文']


class DailyTaskService(ExcelService):
    """每日任务服务 - 每天的任务可以不同"""
    def __init__(self):
        from config import DATA_DIR
        super().__init__(str(DATA_DIR / "daily_tasks.xlsx"))
        self._init_headers()
    
    def _init_headers(self):
        """初始化表头"""
        df = self.read_all()
        if df.empty or 'ID' not in df.columns:
            df = pd.DataFrame(columns=['ID', '日期', '任务名称', '是否完成'])
            df.to_excel(self.file_path, index=False)
    
    def get_next_id(self) -> int:
        """获取下一个全局递增ID"""
        df = self.read_all()
        if df.empty or 'ID' not in df.columns:
            return 1
        if len(df) == 0:
            return 1
        df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
        max_id = df['ID'].max()
        if pd.isna(max_id):
            return 1
        return int(max_id) + 1
    
    def get_tasks_by_date(self, date_str: str) -> List[Dict]:
        """获取指定日期的所有任务"""
        df = self.read_all()
        if df.empty:
            return []
        
        # 筛选指定日期的任务
        df_filtered = df[df['日期'] == date_str]
        return df_filtered.to_dict('records')
    
    def add_task(self, date_str: str, task_name: str, completed: bool = False) -> int:
        """添加新任务"""
        task_id = self.get_next_id()
        data = {
            'ID': task_id,
            '日期': date_str,
            '任务名称': task_name,
            '是否完成': completed
        }
        self.append_row(data)
        return task_id
    
    def update_task_status(self, task_id: int, completed: bool):
        """更新任务完成状态"""
        df = self.read_all()
        if df.empty:
            return
        
        # 找到对应的任务并更新
        df.loc[df['ID'] == task_id, '是否完成'] = completed
        df.to_excel(self.file_path, index=False)
    
    def update_tasks_for_date(self, date_str: str, completed_task_ids: List[int]):
        """批量更新指定日期的任务完成状态"""
        df = self.read_all()
        if df.empty:
            return
        
        # 将该日期的所有任务设为未完成
        df.loc[df['日期'] == date_str, '是否完成'] = False
        
        # 将指定ID的任务设为已完成
        df.loc[(df['日期'] == date_str) & (df['ID'].isin(completed_task_ids)), '是否完成'] = True
        
        df.to_excel(self.file_path, index=False)
    
    def delete_task(self, task_id: int):
        """删除任务"""
        df = self.read_all()
        if df.empty:
            return
        
        df = df[df['ID'] != task_id]
        df.to_excel(self.file_path, index=False)
    
    def init_default_tasks_for_date(self, date_str: str):
        """为指定日期初始化默认任务（如果该日期还没有任务）"""
        existing_tasks = self.get_tasks_by_date(date_str)
        
        if not existing_tasks:
            # 添加默认任务
            default_tasks = [
                '数学练习',
                '英语阅读',
                '专业课复习',
                '错题整理',
            ]
            for task_name in default_tasks:
                self.add_task(date_str, task_name, completed=False)


class StudyRecordService(ExcelService):
    """学习记录服务 - 只记录学习时长"""
    def __init__(self):
        from config import DATA_DIR
        super().__init__(str(DATA_DIR / "study_records.xlsx"))
        self._init_headers()
    
    def _init_headers(self):
        """初始化表头"""
        df = self.read_all()
        if df.empty or '日期' not in df.columns:
            df = pd.DataFrame(columns=['日期', '学习时长(小时)'])
            df.to_excel(self.file_path, index=False)
    
    def get_record_by_date(self, date_str: str) -> Optional[Dict]:
        """根据日期获取记录"""
        df = self.read_all()
        if df.empty:
            return None
        
        result = df[df['日期'] == date_str]
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()
    
    def save_record(self, date_str: str, study_hours: float):
        """保存或更新学习记录"""
        df = self.read_all()
        
        # 检查是否已存在该日期的记录
        if not df.empty and date_str in df['日期'].values:
            # 更新现有记录
            idx = df[df['日期'] == date_str].index[0]
            df.at[idx, '学习时长(小时)'] = study_hours
            df.to_excel(self.file_path, index=False)
        else:
            # 添加新记录
            data = {
                '日期': date_str,
                '学习时长(小时)': study_hours
            }
            self.append_row(data)
    
    def get_records_by_range(self, start_date: str, end_date: str) -> List[Dict]:
        """获取指定日期范围的记录"""
        df = self.read_all()
        if df.empty:
            return []
        
        df['日期'] = pd.to_datetime(df['日期'])
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        result = df[(df['日期'] >= start) & (df['日期'] <= end)]
        result = result.sort_values('日期', ascending=True)
        
        return result.to_dict('records')
