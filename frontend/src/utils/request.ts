import Taro from '@tarojs/taro';

const BASE_URL = 'http://localhost:8080/api';

// Token存储键名
const TOKEN_KEY = 'prep_keeper_token';
const REFRESH_TOKEN_KEY = 'prep_keeper_refresh_token';

// 获取存储的Token
export const getToken = async (): Promise<string | null> => {
  try {
    return await Taro.getStorageSync(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const getRefreshToken = async (): Promise<string | null> => {
  try {
    return await Taro.getStorageSync(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
};

// 存储Token
export const setToken = async (token: string, refreshToken?: string): Promise<void> => {
  try {
    await Taro.setStorageSync(TOKEN_KEY, token);
    if (refreshToken) {
      await Taro.setStorageSync(REFRESH_TOKEN_KEY, refreshToken);
    }
  } catch (e) {
    console.error('存储Token失败', e);
  }
};

// 清除Token
export const clearToken = async (): Promise<void> => {
  try {
    await Taro.removeStorageSync(TOKEN_KEY);
    await Taro.removeStorageSync(REFRESH_TOKEN_KEY);
  } catch (e) {
    console.error('清除Token失败', e);
  }
};

// 通用请求函数
export const request = async <T>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any,
  needAuth = true
): Promise<T> => {
  const header: Record<string, string> = {
    'Content-Type': 'application/json'
  };

  if (needAuth) {
    const token = await getToken();
    if (token) {
      header['Authorization'] = `Bearer ${token}`;
    }
  }

  try {
    const response = await Taro.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      timeout: 30000
    });

    const result = response.data as any;

    if (result.code !== 0) {
      // Token过期处理
      if (result.code === 3002) {
        await clearToken();
        Taro.navigateTo({ url: '/pages/login/index' });
        throw new Error('登录已过期，请重新登录');
      }
      throw new Error(result.message || '请求失败');
    }

    return result.data as T;
  } catch (error: any) {
    console.error('请求错误:', error);
    Taro.showToast({
      title: error.message || '网络请求失败',
      icon: 'error',
      duration: 2000
    });
    throw error;
  }
};

// 不带认证的请求
export const requestWithoutAuth = async <T>(
  url: string,
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
  data?: any
): Promise<T> => {
  return request<T>(url, method, data, false);
};