import client from './client'
import type { ApiResponse, PlanCreateRequest, PlanResponse, SupervisionMode } from '@/types'

export const planApi = {
  create: (data: PlanCreateRequest) =>
    client.post<ApiResponse<PlanResponse>>('/plans', data),

  getById: (planId: string) =>
    client.get<ApiResponse<PlanResponse>>(`/plans/${planId}`),

  getByUser: (userId: string) =>
    client.get<ApiResponse<PlanResponse[]>>(`/plans/user/${userId}`),

  switchMode: (planId: string, mode: SupervisionMode) =>
    client.put<ApiResponse<PlanResponse>>(`/plans/${planId}/mode`, null, {
      params: { mode },
    }),

  deletePlan: (planId: string) =>
    client.delete<ApiResponse<void>>(`/plans/${planId}`),

  createWithTasks: (data: {
    examName: string
    examType: string
    examDate: string
    dailyHours: number
    foundationLevel: number
    weakSubjects: string[]
    currentMode: number
    tasks: Array<{
      taskDate: string
      subject: string
      taskContent: string
      estimatedMinutes: number
      taskType: number
      phase: number
    }>
  }) => client.post<ApiResponse<PlanResponse>>('/plans/with-tasks', data),
}
