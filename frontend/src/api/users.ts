import client from './client'
import type { ApiResponse, User } from '@/types'

export const userApi = {
  getById: (userId: string) =>
    client.get<ApiResponse<User>>(`/users/${userId}`),

  update: (userId: string, data: Partial<Pick<User, 'nickname' | 'avatarUrl'>>) =>
    client.put<ApiResponse<User>>(`/users/${userId}`, data),

  getStats: (userId: string) =>
    client.get<ApiResponse<{ totalCheckins: number; currentStreak: number; maxStreak: number }>>(
      `/users/${userId}/stats`
    ),
}
