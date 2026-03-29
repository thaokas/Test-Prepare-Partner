import { create } from 'zustand';
import { StudyPlan, SupervisionMode, PlanCreateRequest } from '@/types';
import * as planApi from '@/services/plan';

interface PlanState {
  plans: StudyPlan[];
  currentPlan: StudyPlan | null;
  isLoading: boolean;

  // Actions
  fetchUserPlans: (userId: string) => Promise<void>;
  fetchPlanById: (planId: string) => Promise<void>;
  createPlan: (data: PlanCreateRequest) => Promise<StudyPlan>;
  updatePlanMode: (planId: string, mode: SupervisionMode) => Promise<void>;
  deletePlan: (planId: string) => Promise<void>;
  setCurrentPlan: (plan: StudyPlan | null) => void;
  clearPlans: () => void;
}

export const usePlanStore = create<PlanState>((set, get) => ({
  plans: [],
  currentPlan: null,
  isLoading: false,

  fetchUserPlans: async (userId: string) => {
    set({ isLoading: true });
    try {
      const plans = await planApi.getUserPlans(userId);
      set({ plans, isLoading: false });
      // 如果有计划但没有当前计划，设置第一个为当前计划
      if (plans.length > 0 && !get().currentPlan) {
        set({ currentPlan: plans[0] });
      }
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  fetchPlanById: async (planId: string) => {
    set({ isLoading: true });
    try {
      const plan = await planApi.getPlanById(planId);
      set({ currentPlan: plan, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  createPlan: async (data: PlanCreateRequest) => {
    set({ isLoading: true });
    try {
      const newPlan = await planApi.createPlan(data);
      set((state) => ({
        plans: [...state.plans, newPlan],
        currentPlan: newPlan,
        isLoading: false
      }));
      return newPlan;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  updatePlanMode: async (planId: string, mode: SupervisionMode) => {
    set({ isLoading: true });
    try {
      const updatedPlan = await planApi.updatePlanMode(planId, mode);
      set((state) => ({
        plans: state.plans.map((p) =>
          p.planId === planId ? updatedPlan : p
        ),
        currentPlan: state.currentPlan?.planId === planId
          ? updatedPlan
          : state.currentPlan,
        isLoading: false
      }));
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  deletePlan: async (planId: string) => {
    set({ isLoading: true });
    try {
      await planApi.deletePlan(planId);
      set((state) => {
        const newPlans = state.plans.filter((p) => p.planId !== planId);
        return {
          plans: newPlans,
          currentPlan: state.currentPlan?.planId === planId
            ? newPlans[0] || null
            : state.currentPlan,
          isLoading: false
        };
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  setCurrentPlan: (plan: StudyPlan | null) => {
    set({ currentPlan: plan });
  },

  clearPlans: () => {
    set({ plans: [], currentPlan: null });
  }
}));