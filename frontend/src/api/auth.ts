import client from './client'
import type { ApiResponse, AuthResponse, LoginRequest, RegisterRequest, User } from '@/types'

export const authApi = {
  register: (data: RegisterRequest) =>
    client.post<ApiResponse<AuthResponse>>('/auth/register', data),

  login: (data: LoginRequest) =>
    client.post<ApiResponse<AuthResponse>>('/auth/login', data),

  refresh: (refreshToken: string) =>
    client.post<ApiResponse<{ accessToken: string }>>('/auth/refresh', { refreshToken }),

  me: () =>
    client.get<ApiResponse<User>>('/auth/me'),
}
