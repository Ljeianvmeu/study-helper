import axios from 'axios';
import type {
  ScoreListResponse,
  ScoreCreateRequest,
  ChartDataResponse,
  EssayAnalysisResponse,
  DailyTasksResponse,
  TaskCreateRequest,
  StudyRecordCreateRequest,
  ChartDataPoint,
  ChatRequest,
  ChatResponse,
} from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== 分数统计API ====================
export const scoresAPI = {
  getPaperTypes: (subject: string) =>
    apiClient.get<{ paper_types: string[] }>(`/paper-types?subject=${subject}`),

  createScore: (data: ScoreCreateRequest) => apiClient.post('/scores', data),

  getScores: (params: {
    subject?: string;
    paper_type?: string;
    page?: number;
    page_size?: number;
  }) => apiClient.get<ScoreListResponse>('/scores', { params }),

  updateScore: (id: number, data: Partial<ScoreCreateRequest>) =>
    apiClient.put(`/scores/${id}`, data),

  deleteScore: (id: number) => apiClient.delete(`/scores/${id}`),

  getChartData: (subject: string, paper_type?: string) =>
    apiClient.get<ChartDataResponse>('/scores/chart-data', {
      params: { subject, paper_type },
    }),
};

// ==================== 英语作文API ====================
export const essaysAPI = {
  getTopics: () => apiClient.get<{ years: number[]; essay_types: string[] }>('/essays/topics'),

  getTopicDetail: (year: number, essayType: string) =>
    apiClient.get(`/essays/topics/${year}/${essayType}`),

  getTopicImage: (year: number, essayType: string) =>
    `${API_BASE_URL}/essays/topics/image/${year}/${essayType}`,

  addTopic: (formData: FormData) =>
    apiClient.post('/essays/topics', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  deleteTopic: (year: number, essayType: string) =>
    apiClient.delete(`/essays/topics/${year}/${essayType}`),

  // 第一步：OCR识别作文图片
  ocrEssay: (formData: FormData) =>
    apiClient.post('/essays/ocr', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // 第二步：优化作文
  analyzeEssay: (data: any) =>
    apiClient.post<EssayAnalysisResponse>('/essays/analyze', data, {
      headers: {
        'Content-Type': 'application/json',
      },
    }),

  saveAnalysis: (year: number, data: any) =>
    apiClient.post('/essays/save', { year, data }),
};

// ==================== 每日任务API ====================
export const tasksAPI = {
  getTasksByDate: (date: string) =>
    apiClient.get<DailyTasksResponse>(`/tasks/by-date?date=${date}`),

  addTask: (data: TaskCreateRequest) =>
    apiClient.post('/tasks/add', data),

  deleteTask: (taskId: number) =>
    apiClient.delete(`/tasks/${taskId}`),

  saveStudyRecord: (data: StudyRecordCreateRequest) => 
    apiClient.post('/tasks/save', data),

  updateStudyRecord: (data: StudyRecordCreateRequest) => 
    apiClient.put('/tasks/record', data),

  getChartData: (view: 'week' | 'month' | 'all') =>
    apiClient.get<{ data: ChartDataPoint[] }>(`/tasks/chart-data?view=${view}`),
};

// ==================== 通用AI API ====================
export const aiAPI = {
  chat: (data: ChatRequest) => apiClient.post<ChatResponse>('/chat', data),
};

// ==================== 系统配置API ====================
export const systemAPI = {
  // 获取系统状态
  getStatus: () =>
    apiClient.get<{
      api_configured: boolean;
      daily_tasks_exists: boolean;
    }>('/system/status'),

  // 保存API密钥
  saveAPIKeys: (data: {
    modelscope_api_key: string;
    dashscope_api_key: string;
  }) =>
    apiClient.post<{
      success: boolean;
      message: string;
    }>('/system/api-keys', data),

  // 上传 daily_tasks.xlsx
  uploadDailyTasks: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post<{
      success: boolean;
      message: string;
    }>('/system/upload-daily-tasks', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 清理临时文件
  cleanupTemp: () =>
    apiClient.delete<{
      success: boolean;
      message: string;
    }>('/system/cleanup-temp'),
};

export default apiClient;
