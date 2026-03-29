import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { useTaskStore } from '@/store/task';
import { TaskStatus } from '@/types';
import './index.scss';

export default function TaskPage() {
  const { currentPlan } = usePlanStore();
  const { todayTasks, fetchTodayTasks, completeTask, updateTaskStatus } = useTaskStore();

  useEffect(() => {
    const planId = Taro.getCurrentInstance().router?.params?.planId || currentPlan?.planId;
    if (planId) {
      fetchTodayTasks(planId);
    }
  }, [currentPlan]);

  const handleCompleteTask = async (taskId: string) => {
    try {
      await completeTask(taskId);
      Taro.showToast({ title: '任务已完成', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '操作失败', icon: 'error' });
    }
  };

  const handleSkipTask = async (taskId: string) => {
    try {
      await updateTaskStatus(taskId, TaskStatus.Skipped);
      Taro.showToast({ title: '任务已跳过', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '操作失败', icon: 'error' });
    }
  };

  const getTaskTypeText = (taskType: number) => {
    const types = ['', '学习', '复习', '刷题', '模考'];
    return types[taskType] || '';
  };

  const getPhaseText = (phase: number) => {
    const phases = ['', '基础阶段', '强化阶段', '冲刺阶段'];
    return phases[phase] || '';
  };

  const completedCount = todayTasks.filter(t => t.status === TaskStatus.Completed).length;
  const totalCount = todayTasks.length;

  return (
    <View className='task-page'>
      {/* 进度概览 */}
      <View className='progress-overview'>
        <View className='progress-circle'>
          <View className='progress-value'>
            {totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0}%
          </View>
        </View>
        <View className='progress-info'>
          <View className='progress-text'>
            今日已完成 {completedCount}/{totalCount} 个任务
          </View>
          <View className='progress-bar'>
            <View
              className='progress-fill'
              style={{ width: `${totalCount > 0 ? (completedCount / totalCount) * 100 : 0}%` }}
            />
          </View>
        </View>
      </View>

      {/* 任务列表 */}
      <View className='task-list card'>
        <View className='section-title'>今日任务</View>

        {todayTasks.length === 0 ? (
          <View className='empty-tasks'>
            <View className='empty-icon'>📋</View>
            <View className='empty-text'>今日暂无任务安排</View>
          </View>
        ) : (
          <View className='tasks'>
            {todayTasks.map(task => (
              <View
                key={task.taskId}
                className={`task-card ${task.status === TaskStatus.Completed ? 'completed' : ''} ${task.status === TaskStatus.Skipped ? 'skipped' : ''}`}
              >
                <View className='task-header'>
                  <View className='task-type-tag'>{getTaskTypeText(task.taskType)}</View>
                  <View className='task-phase-tag'>{getPhaseText(task.phase)}</View>
                </View>

                <View className='task-body'>
                  <View className='task-subject'>{task.subject}</View>
                  <View className='task-content'>{task.taskContent}</View>
                  <View className='task-time'>
                    预计时长：{task.estimatedMinutes || 30}分钟
                  </View>
                </View>

                <View className='task-footer'>
                  {task.status === TaskStatus.NotStarted && (
                    <>
                      <View
                        className='action-btn complete'
                        onClick={() => handleCompleteTask(task.taskId)}
                      >
                        完成
                      </View>
                      <View
                        className='action-btn skip'
                        onClick={() => handleSkipTask(task.taskId)}
                      >
                        跳过
                      </View>
                    </>
                  )}
                  {task.status === TaskStatus.Completed && (
                    <View className='status-tag completed'>已完成 ✓</View>
                  )}
                  {task.status === TaskStatus.Skipped && (
                    <View className='status-tag skipped'>已跳过</View>
                  )}
                  {task.status === TaskStatus.InProgress && (
                    <View
                      className='action-btn complete'
                      onClick={() => handleCompleteTask(task.taskId)}
                    >
                      完成
                    </View>
                  )}
                </View>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* 快捷操作 */}
      <View className='quick-actions'>
        <View
          className='action-card'
          onClick={() => Taro.navigateTo({ url: '/pages/checkin/index' })}
        >
          <View className='action-icon'>✅</View>
          <View className='action-text'>去打卡</View>
        </View>
        <View
          className='action-card'
          onClick={() => Taro.navigateTo({ url: '/pages/chat/index' })}
        >
          <View className='action-icon'>🤖</View>
          <View className='action-text'>AI助手</View>
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '今日任务'
});