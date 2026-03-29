import { request } from '@/utils/request';
import { Task, TaskStatus } from '@/types';

// 获取今日任务
export const getTodayTasks = async (planId: string): Promise<Task[]> => {
  return request<Task[]>(`/tasks/today?planId=${planId}`, 'GET');
};

// 获取计划下所有任务
export const getTasksByPlan = async (planId: string): Promise<Task[]> => {
  return request<Task[]>(`/tasks/plan/${planId}`, 'GET');
};

// 更新任务状态
export const updateTaskStatus = async (
  taskId: string,
  status: TaskStatus
): Promise<Task> => {
  return request<Task>(`/tasks/${taskId}/status?status=${status}`, 'PUT');
};

// 完成单个任务
export const completeTask = async (taskId: string): Promise<Task> => {
  return request<Task>(`/tasks/${taskId}/complete`, 'POST');
};

// 批量完成任务
export const batchCompleteTasks = async (taskIds: string[]): Promise<Task[]> => {
  const results: Task[] = [];
  for (const taskId of taskIds) {
    const task = await completeTask(taskId);
    results.push(task);
  }
  return results;
};

// 获取任务统计（按日期）
export const getTaskStatsByDate = async (
  planId: string,
  startDate: string,
  endDate: string
): Promise<Record<string, { completed: number; total: number }>> => {
  const allTasks = await getTasksByPlan(planId);
  const stats: Record<string, { completed: number; total: number }> = {};

  allTasks.forEach(task => {
    if (task.taskDate >= startDate && task.taskDate <= endDate) {
      if (!stats[task.taskDate]) {
        stats[task.taskDate] = { completed: 0, total: 0 };
      }
      stats[task.taskDate].total++;
      if (task.status === TaskStatus.Completed) {
        stats[task.taskDate].completed++;
      }
    }
  });

  return stats;
};