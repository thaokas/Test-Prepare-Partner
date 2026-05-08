import client from './client'
import type { ApiResponse, PlanChatRequest, PlanChatResponse, WeeklyReportRequest, WeeklyReportResponse } from '@/types'

export const agentApi = {
  planChat: (data: PlanChatRequest) =>
    client.post<ApiResponse<PlanChatResponse>>('/agent/plan/chat', data),

  getWeeklyReport: (data: WeeklyReportRequest) =>
    client.post<ApiResponse<WeeklyReportResponse>>('/agent/report/weekly', data),
}
