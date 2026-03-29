import { request } from '@/utils/request';
import { Checkin, CheckinRequest } from '@/types';

// 提交打卡
export const submitCheckin = async (data: CheckinRequest): Promise<Checkin> => {
  return request<Checkin>('/checkins', 'POST', data);
};

// 获取今日打卡记录
export const getTodayCheckin = async (planId: string): Promise<Checkin | null> => {
  return request<Checkin | null>(`/checkins/today?planId=${planId}`, 'GET');
};

// 获取打卡历史
export const getCheckinHistory = async (
  startDate?: string,
  endDate?: string
): Promise<Checkin[]> => {
  const params = new URLSearchParams();
  if (startDate) params.append('startDate', startDate);
  if (endDate) params.append('endDate', endDate);
  return request<Checkin[]>(`/checkins/history?${params.toString()}`, 'GET');
};

// 获取连续打卡天数
export const getCheckinStreak = async (): Promise<number> => {
  return request<number>('/checkins/streak', 'GET');
};

// 补卡
export const makeupCheckin = async (
  planId: string,
  checkinDate: string,
  completedTaskIds: string[]
): Promise<Checkin> => {
  return request<Checkin>('/checkins', 'POST', {
    planId,
    checkinDate,
    completedTaskIds,
    isMakeup: true
  });
};