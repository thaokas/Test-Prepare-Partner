import { requestWithoutAuth, request, setToken, clearToken } from '@/utils/request';
import {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  User,
  ApiResponse
} from '@/types';

// 用户注册
export const register = async (data: RegisterRequest): Promise<AuthResponse> => {
  const response = await requestWithoutAuth<ApiResponse<AuthResponse>>(
    '/auth/register',
    'POST',
    data
  );
  // 注册成功后存储Token
  if (response.data) {
    await setToken(response.data.accessToken, response.data.refreshToken);
  }
  return response.data;
};

// 用户登录
export const login = async (data: LoginRequest): Promise<AuthResponse> => {
  const response = await requestWithoutAuth<ApiResponse<AuthResponse>>(
    '/auth/login',
    'POST',
    data
  );
  // 登录成功后存储Token
  if (response.data) {
    await setToken(response.data.accessToken, response.data.refreshToken);
  }
  return response.data;
};

// 刷新Token
export const refreshToken = async (token: string): Promise<AuthResponse> => {
  const response = await requestWithoutAuth<ApiResponse<AuthResponse>>(
    '/auth/refresh',
    'POST',
    token
  );
  if (response.data) {
    await setToken(response.data.accessToken, response.data.refreshToken);
  }
  return response.data;
};

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User> => {
  return request<User>('/auth/me', 'GET');
};

// 登出
export const logout = async (): Promise<void> => {
  await clearToken();
};