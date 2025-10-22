// ==================== 分数统计模块 ====================
export interface Score {
  id: number;
  subject: '数学' | '专业课' | '英语';
  year: number;
  paper_type: string;
  score: number;
  input_date: string;
}

export interface ScoreListResponse {
  total: number;
  page: number;
  page_size: number;
  data: Score[];
}

export interface ScoreCreateRequest {
  subject: '数学' | '专业课' | '英语';
  year: number;
  paper_type: string;
  score: number;
  input_date: string;
}

export interface ChartDataResponse {
  dates: string[];
  scores: number[];
  subject: string;
  message?: string;
}

// ==================== 英语作文模块 ====================
export interface EssayAnalysisRequest {
  year: number;
  image: File;
}

export interface EssayAnalysisResponse {
  topic: string;
  reference_essay: string;
  original_text: string;
  optimized_text: string;
  score?: {  // 添加打分字段
    level: string;
    points: number;
  };
  suggestions: {
    topic_relevance?: string;  // 兼容旧版本字段
    topic_compliance?: string[];  // 新版本字段（题意符合度）
    spelling_errors: string[];
    grammar_errors: string[];
    word_optimization: string[];
    sentence_optimization: string[];
    structure_optimization: string | string[];  // 可以是字符串或数组
  };
}

// ==================== 每日任务模块 ====================
export interface DailyTask {
  id: number;
  date: string;
  task_name: string;
  completed: boolean;
}

export interface TaskCreateRequest {
  date: string;
  task_name: string;
}

export interface StudyRecordCreateRequest {
  date: string;
  study_hours: number;
  study_minutes: number;
  completed_task_ids: number[];
}

export interface DailyTasksResponse {
  date: string;
  study_hours: number;
  total_tasks: number;
  completed_tasks: number;
  completion_rate: number;
  tasks: DailyTask[];
}

export interface ChartDataPoint {
  date: string;
  study_hours: number;
  completion_rate: number;
}

// ==================== 通用AI模块 ====================
export interface ChatMessage {
  sender: 'user' | 'ai';
  text: string;
}

export interface ChatRequest {
  prompt: string;
}

export interface ChatResponse {
  response: string;
}
