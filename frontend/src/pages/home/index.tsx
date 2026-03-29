import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { useTaskStore } from '@/store/task';
import { TaskStatus } from '@/types';
import './index.scss';

export default function HomePage() {
  const { user, fetchCurrentUser, isLoggedIn } = useUserStore();
  const { plans, currentPlan, fetchUserPlans } = usePlanStore();
  const { todayTasks, fetchTodayTasks, completeTask, currentStreak, fetchCheckinStreak } = useTaskStore();

  useEffect(() => {
    if (!isLoggedIn) {
      Taro.redirectTo({ url: '/pages/login/index' });
      return;
    }
    init();
  }, [isLoggedIn]);

  const init = async () => {
    try {
      if (!user) {
        await fetchCurrentUser();
      }
      if (user && plans.length === 0) {
        await fetchUserPlans(user.userId);
      }
      if (currentPlan) {
        await fetchTodayTasks(currentPlan.planId);
        await fetchCheckinStreak();
      }
    } catch (error) {
      console.error('初始化失败', error);
    }
  };

  // 如果没有计划，显示创建计划提示
  if (!currentPlan) {
    return (
      <View className='home-page empty'>
        <View className='empty-content'>
          <View className='empty-icon'>📋</View>
          <View className='empty-title'>还没有学习计划</View>
          <View className='empty-desc'>创建一个计划，开始你的备考之旅吧</View>
          <View className='create-btn' onClick={() => Taro.navigateTo({ url: '/pages/plan/create/index' })}>
            创建计划
          </View>
        </View>
      </View>
    );
  }

  // 计算今日任务完成情况
  const completedCount = todayTasks.filter(t => t.status === TaskStatus.Completed).length;
  const totalCount = todayTasks.length;
  const completionRate = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0;

  const handleTaskClick = async (taskId: string) => {
    try {
      await completeTask(taskId);
      Taro.showToast({ title: '任务已完成', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '操作失败', icon: 'error' });
    }
  };

  return (
    <View className='home-page'>
      {/* 欢迎区域 */}
      <View className='welcome-section'>
        <View className='greeting'>
          <Text className='hi'>Hi, </Text>
          <Text className='nickname'>{user?.nickname || '备考人'}</Text>
        </View>
        <View className='date-info'>
          <Text>今天是 {new Date().toLocaleDateString('zh-CN')}</Text>
        </View>
      </View>

      {/* 统计卡片 */}
      <View className='stats-section'>
        <View className='stat-card streak'>
          <View className='stat-value'>{currentStreak}</View>
          <View className='stat-label'>连续打卡</View>
        </View>
        <View className='stat-card progress'>
          <View className='stat-value'>{completionRate}%</View>
          <View className='stat-label'>今日进度</View>
        </View>
        <View className='stat-card days'>
          <View className='stat-value'>
            {Math.ceil((new Date(currentPlan.examDate).getTime() - Date.now()) / (1000 * 60 * 60 * 24))}
          </View>
          <View className='stat-label'>距离考试</View>
        </View>
      </View>

      {/* 当前计划信息 */}
      <View className='plan-info card'>
        <View className='plan-header'>
          <View className='plan-name'>{currentPlan.examName}</View>
          <View className='plan-type'>{currentPlan.examType}</View>
        </View>
        <View className='plan-progress'>
          <View className='progress-bar'>
            <View className='progress-fill' style={{ width: `${currentPlan.completionRate * 100}%` }} />
          </View>
          <View className='progress-text'>
            已完成 {currentPlan.completedTasks}/{currentPlan.totalTasks} 任务
          </View>
        </View>
      </View>

      {/* 今日任务 */}
      <View className='today-tasks card'>
        <View className='section-header'>
          <View className='section-title'>今日任务</View>
          <View className='task-count'>{completedCount}/{totalCount}</View>
        </View>

        {todayTasks.length === 0 ? (
          <View className='no-tasks'>今日暂无任务安排</View>
        ) : (
          <View className='task-list'>
            {todayTasks.map(task => (
              <View
                key={task.taskId}
                className={`task-item ${task.status === TaskStatus.Completed ? 'completed' : ''}`}
                onClick={() => handleTaskClick(task.taskId)}
              >
                <View className='task-checkbox'>
                  {task.status === TaskStatus.Completed ? '✓' : ''}
                </View>
                <View className='task-content'>
                  <View className='task-subject'>{task.subject}</View>
                  <View className='task-text'>{task.taskContent}</View>
                  <View className='task-meta'>
                    <Text className='task-time'>{task.estimatedMinutes}分钟</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* 快捷操作 */}
      <View className='quick-actions'>
        <View className='action-btn' onClick={() => Taro.navigateTo({ url: '/pages/checkin/index' })}>
          打卡
        </View>
        <View className='action-btn' onClick={() => Taro.navigateTo({ url: '/pages/chat/index' })}>
          AI助手
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '备考搭子'
});