import client from './client'
import type { ApiResponse, Reminder, ReminderSettingsResponse, ReminderConfigRequest, PlanResponse } from '@/types'

export const reminderApi = {
  getAll: () =>
    client.get<ApiResponse<Reminder[]>>('/reminders'),

  getSettings: () =>
    client.get<ApiResponse<ReminderSettingsResponse>>('/reminders/settings'),

  updateConfig: (data: ReminderConfigRequest) =>
    client.put<ApiResponse<PlanResponse>>('/reminders/config', data),

  getHistory: () =>
    client.get<ApiResponse<Reminder[]>>('/reminders/history'),
}
