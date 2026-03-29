import { request } from '@/utils/request';

// Agent对话
export const chatWithAgent = async (
  userId: string,
  message: string
): Promise<{ response: string; suggestions?: string[] }> => {
  return request('/agent/chat', 'POST', { userId, message });
};

// 生成计划
export const generatePlan = async (params: {
  examName: string;
  examType: string;
  examDate: string;
  dailyHours: number;
  foundationLevel: number;
  weakSubjects?: string[];
}): Promise<{ planContent: string; suggestions: string[] }> => {
  return request('/agent/generate-plan', 'POST', params);
};

// 获取周报
export const getWeeklyReport = async (userId: string): Promise<{
  summary: string;
  completedTasks: number;
  totalTasks: number;
  streakDays: number;
  suggestions: string[];
}> => {
  return request(`/agent/report/weekly?userId=${userId}`, 'GET');
};