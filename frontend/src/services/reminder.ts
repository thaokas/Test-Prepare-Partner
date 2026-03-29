import { request } from '@/utils/request';
import { Reminder, ReminderConfigRequest } from '@/types';

// 获取提醒列表
export const getReminders = async (): Promise<Reminder[]> => {
  return request<Reminder[]>('/reminders', 'GET');
};

// 配置提醒设置
export const configReminder = async (
  data: ReminderConfigRequest
): Promise<Reminder> => {
  return request<Reminder>('/reminders/config', 'PUT', data);
};

// 获取提醒历史
export const getReminderHistory = async (
  startDate?: string,
  endDate?: string
): Promise<Reminder[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('startDate', startDate);
  if (endDate) params.append('endDate', endDate);
  return request<Reminder[]>(`/reminders/history?${params.toString()}`, 'GET');
};