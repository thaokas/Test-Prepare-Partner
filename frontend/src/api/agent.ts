import client from './client'
import type { ApiResponse, PlanChatRequest, PlanChatResponse, WeeklyReportRequest, WeeklyReportResponse } from '@/types'

export const agentApi = {
  planChat: (data: PlanChatRequest) =>
    client.post<ApiResponse<PlanChatResponse>>('/agent/plan/chat', data),

  getWeeklyReport: (data: WeeklyReportRequest) =>
    client.post<ApiResponse<WeeklyReportResponse>>('/agent/report/weekly', data),

  llmChat: (data: { messages: Array<{ role: string; content: string }>; system_prompt: string }) =>
    client.post<ApiResponse<{ content: string; error?: string }>>('/agent/llm/chat', data),

  search: (data: { query: string }) =>
    client.post<ApiResponse<{ results: Array<{ title: string; snippet: string; url: string }>; error?: string }>>('/agent/search', data),
}
