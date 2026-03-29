import { request } from '@/utils/request';
import {
  StudyPlan,
  PlanCreateRequest,
  SupervisionMode
} from '@/types';

// 创建计划
export const createPlan = async (data: PlanCreateRequest): Promise<StudyPlan> => {
  return request<StudyPlan>('/plans', 'POST', data);
};

// 获取计划详情
export const getPlanById = async (planId: string): Promise<StudyPlan> => {
  return request<StudyPlan>(`/plans/${planId}`, 'GET');
};

// 获取用户计划列表
export const getUserPlans = async (userId: string): Promise<StudyPlan[]> => {
  return request<StudyPlan[]>(`/plans/user/${userId}`, 'GET');
};

// 切换监督模式
export const updatePlanMode = async (
  planId: string,
  mode: SupervisionMode
): Promise<StudyPlan> => {
  return request<StudyPlan>(`/plans/${planId}/mode?mode=${mode}`, 'PUT');
};

// 删除计划
export const deletePlan = async (planId: string): Promise<void> => {
  return request<void>(`/plans/${planId}`, 'DELETE');
};

// 获取计划统计信息
export const getPlanStats = async (planId: string): Promise<{
  totalTasks: number;
  completedTasks: number;
  completionRate: number;
  currentStreak: number;
}> => {
  const plan = await getPlanById(planId);
  return {
    totalTasks: plan.totalTasks,
    completedTasks: plan.completedTasks,
    completionRate: plan.completionRate,
    currentStreak: 0 // 需要从用户信息获取
  };
};