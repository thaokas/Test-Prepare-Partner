import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { PlanStatus, SupervisionMode } from '@/types';
import './index.scss';

export default function PlanPage() {
  const { user, isLoggedIn } = useUserStore();
  const { plans, currentPlan, fetchUserPlans, setCurrentPlan, deletePlan, isLoading } = usePlanStore();

  useEffect(() => {
    if (!isLoggedIn) {
      Taro.redirectTo({ url: '/pages/login/index' });
      return;
    }
    if (user && plans.length === 0) {
      fetchUserPlans(user.userId);
    }
  }, [isLoggedIn, user]);

  const handleCreatePlan = () => {
    Taro.navigateTo({ url: '/pages/plan/create/index' });
  };

  const handlePlanClick = (planId: string) => {
    setCurrentPlan(plans.find(p => p.planId === planId) || null);
    Taro.navigateTo({ url: `/pages/plan/detail/index?id=${planId}` });
  };

  const handleDeletePlan = async (planId: string) => {
    try {
      await deletePlan(planId);
      Taro.showToast({ title: '删除成功', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '删除失败', icon: 'error' });
    }
  };

  const getStatusText = (status: PlanStatus) => {
    const statusMap = {
      [PlanStatus.InProgress]: '进行中',
      [PlanStatus.Completed]: '已完成',
      [PlanStatus.Paused]: '已暂停'
    };
    return statusMap[status] || '未知';
  };

  const getModeText = (mode: SupervisionMode) => {
    const modeMap = {
      [SupervisionMode.Silent]: '静默',
      [SupervisionMode.Gentle]: '温柔',
      [SupervisionMode.Intensive]: '强化',
      [SupervisionMode.TangSeng]: '唐僧'
    };
    return modeMap[mode] || '未知';
  };

  const getDaysRemaining = (examDate: string) => {
    const diff = new Date(examDate).getTime() - Date.now();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  return (
    <View className='plan-page'>
      {/* 页面头部 */}
      <View className='page-header'>
        <View className='title'>我的计划</View>
        <View className='create-btn' onClick={handleCreatePlan}>
          + 新计划
        </View>
      </View>

      {/* 计划列表 */}
      {isLoading ? (
        <View className='loading'>加载中...</View>
      ) : plans.length === 0 ? (
        <View className='empty'>
          <View className='empty-icon'>📝</View>
          <View className='empty-text'>还没有学习计划</View>
          <View className='empty-tip'>点击上方按钮创建新计划</View>
        </View>
      ) : (
        <View className='plan-list'>
          {plans.map(plan => (
            <View
              key={plan.planId}
              className={`plan-card ${plan.planId === currentPlan?.planId ? 'active' : ''}`}
              onClick={() => handlePlanClick(plan.planId)}
            >
              <View className='plan-header'>
                <View className='plan-name'>{plan.examName}</View>
                <View className={`plan-status status-${plan.planStatus}`}>
                  {getStatusText(plan.planStatus)}
                </View>
              </View>

              <View className='plan-info'>
                <View className='info-item'>
                  <Text className='label'>考试类型：</Text>
                  <Text className='value'>{plan.examType}</Text>
                </View>
                <View className='info-item'>
                  <Text className='label'>考试日期：</Text>
                  <Text className='value'>{plan.examDate}</Text>
                </View>
                <View className='info-item'>
                  <Text className='label'>监督模式：</Text>
                  <Text className='value mode'>{getModeText(plan.currentMode)}</Text>
                </View>
              </View>

              <View className='plan-progress'>
                <View className='days-left'>
                  <Text className='days'>{getDaysRemaining(plan.examDate)}</Text>
                  <Text className='text'>天</Text>
                </View>
                <View className='progress-info'>
                  <View className='progress-bar'>
                    <View className='progress-fill' style={{ width: `${plan.completionRate * 100}%` }} />
                  </View>
                  <View className='progress-text'>
                    完成 {plan.completedTasks}/{plan.totalTasks} 任务
                  </View>
                </View>
              </View>

              <View className='plan-actions'>
                <View
                  className='action delete'
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeletePlan(plan.planId);
                  }}
                >
                  删除
                </View>
              </View>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '学习计划'
});