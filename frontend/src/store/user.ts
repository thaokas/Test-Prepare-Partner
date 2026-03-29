import { create } from 'zustand';
import { User, StudyPlan, Task, Checkin } from '@/types';
import * as authApi from '@/services/auth';
import * as planApi from '@/services/plan';
import * as taskApi from '@/services/task';
import * as checkinApi from '@/services/checkin';
import Taro from '@tarojs/taro';

interface UserState {
  user: User | null;
  isLoggedIn: boolean;
  isLoading: boolean;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, nickname?: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<void>;
  setUser: (user: User | null) => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  isLoggedIn: false,
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.login({ email, password });
      set({
        user: response.user,
        isLoggedIn: true,
        isLoading: false
      });
      Taro.redirectTo({ url: '/pages/home/index' });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  register: async (email: string, password: string, nickname?: string) => {
    set({ isLoading: true });
    try {
      const response = await authApi.register({ email, password, nickname });
      set({
        user: response.user,
        isLoggedIn: true,
        isLoading: false
      });
      Taro.redirectTo({ url: '/pages/home/index' });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout: async () => {
    await authApi.logout();
    set({ user: null, isLoggedIn: false });
    Taro.redirectTo({ url: '/pages/login/index' });
  },

  fetchCurrentUser: async () => {
    set({ isLoading: true });
    try {
      const user = await authApi.getCurrentUser();
      set({ user, isLoggedIn: true, isLoading: false });
    } catch (error) {
      set({ user: null, isLoggedIn: false, isLoading: false });
    }
  },

  setUser: (user: User | null) => {
    set({ user, isLoggedIn: user !== null });
  }
}));