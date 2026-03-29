import { create } from 'zustand';
import { Task, TaskStatus, Checkin } from '@/types';
import * as taskApi from '@/services/task';
import * as checkinApi from '@/services/checkin';

interface TaskState {
  todayTasks: Task[];
  allTasks: Task[];
  checkinHistory: Checkin[];
  currentStreak: number;
  isLoading: boolean;

  // Actions
  fetchTodayTasks: (planId: string) => Promise<void>;
  fetchTasksByPlan: (planId: string) => Promise<void>;
  completeTask: (taskId: string) => Promise<void>;
  updateTaskStatus: (taskId: string, status: TaskStatus) => Promise<void>;
  fetchCheckinHistory: (startDate?: string, endDate?: string) => Promise<void>;
  fetchCheckinStreak: () => Promise<void>;
  submitCheckin: (planId: string, checkinType: number, content?: string) => Promise<void>;
  clearTasks: () => void;
}

export const useTaskStore = create<TaskState>((set, get) => ({
  todayTasks: [],
  allTasks: [],
  checkinHistory: [],
  currentStreak: 0,
  isLoading: false,

  fetchTodayTasks: async (planId: string) => {
    set({ isLoading: true });
    try {
      const tasks = await taskApi.getTodayTasks(planId);
      set({ todayTasks: tasks, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchTasksByPlan: async (planId: string) => {
    set({ isLoading: true });
    try {
      const tasks = await taskApi.getTasksByPlan(planId);
      set({ allTasks: tasks, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  completeTask: async (taskId: string) => {
    try {
      const updatedTask = await taskApi.completeTask(taskId);
      set((state) => ({
        todayTasks: state.todayTasks.map((t) =>
          t.taskId === taskId ? updatedTask : t
        ),
        allTasks: state.allTasks.map((t) =>
          t.taskId === taskId ? updatedTask : t
        )
      }));
    } catch (error) {
      throw error;
    }
  },

  updateTaskStatus: async (taskId: string, status: TaskStatus) => {
    try {
      const updatedTask = await taskApi.updateTaskStatus(taskId, status);
      set((state) => ({
        todayTasks: state.todayTasks.map((t) =>
          t.taskId === taskId ? updatedTask : t
        ),
        allTasks: state.allTasks.map((t) =>
          t.taskId === taskId ? updatedTask : t
        )
      }));
    } catch (error) {
      throw error;
    }
  },

  fetchCheckinHistory: async (startDate?: string, endDate?: string) => {
    set({ isLoading: true });
    try {
      const history = await checkinApi.getCheckinHistory(startDate, endDate);
      set({ checkinHistory: history, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchCheckinStreak: async () => {
    try {
      const streak = await checkinApi.getCheckinStreak();
      set({ currentStreak: streak });
    } catch (error) {
      // 不中断流程，保持当前值
      console.error('获取连续打卡天数失败', error);
    }
  },

  submitCheckin: async (planId: string, checkinType: number, content?: string) => {
    set({ isLoading: true });
    try {
      const checkin = await checkinApi.submitCheckin({
        planId,
        checkinType,
        content
      });
      set((state) => ({
        checkinHistory: [...state.checkinHistory, checkin],
        isLoading: false
      }));
      // 重新获取连续打卡天数
      await get().fetchCheckinStreak();
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  clearTasks: () => {
    set({
      todayTasks: [],
      allTasks: [],
      checkinHistory: [],
      currentStreak: 0
    });
  }
}));