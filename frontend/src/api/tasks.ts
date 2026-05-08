import client from './client'
import type { ApiResponse, TaskResponse, TaskStatus } from '@/types'

export const taskApi = {
  getToday: (planId: string) =>
    client.get<ApiResponse<TaskResponse[]>>('/tasks/today', { params: { planId } }),

  getByPlan: (planId: string) =>
    client.get<ApiResponse<TaskResponse[]>>(`/tasks/plan/${planId}`),

  updateStatus: (taskId: string, status: TaskStatus) =>
    client.put<ApiResponse<TaskResponse>>(`/tasks/${taskId}/status`, null, {
      params: { status },
    }),

  complete: (taskId: string) =>
    client.post<ApiResponse<TaskResponse>>(`/tasks/${taskId}/complete`),
}
