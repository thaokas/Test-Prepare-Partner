import client from './client'
import type { ApiResponse, CheckinRequest, CheckinResponse, CheckinHistoryItem } from '@/types'

export const checkinApi = {
  submit: (data: CheckinRequest) =>
    client.post<ApiResponse<CheckinResponse>>('/checkins', data),

  getToday: (planId: string) =>
    client.get<ApiResponse<CheckinResponse | null>>('/checkins/today', { params: { planId } }),

  getHistory: (startDate: string, endDate: string) =>
    client.get<ApiResponse<CheckinHistoryItem[]>>('/checkins/history', {
      params: { startDate, endDate },
    }),

  getStreak: () =>
    client.get<ApiResponse<number>>('/checkins/streak'),
}
