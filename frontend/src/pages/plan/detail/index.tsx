import { View, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect, useState } from 'react';
import { usePlanStore } from '@/store/plan';
import { useTaskStore } from '@/store/task';
import { Task, TaskStatus, SupervisionMode } from '@/types';
import './index.scss';

export default function PlanDetailPage() {
  const [planId, setPlanId] = useState('');
  const { currentPlan, fetchPlanById, updatePlanMode } = usePlanStore();
  const { allTasks, fetchTasksByPlan } = useTaskStore();

  useEffect(() => {
    const id = Taro.getCurrentInstance().router?.params?.id;
    if (id) {
      setPlanId(id);
      fetchPlanById(id);
      fetchTasksByPlan(id);
    }
  }, []);

  const handleModeChange = async (mode: SupervisionMode) => {
    if (!currentPlan) return;
    try {
      await updatePlanMode(currentPlan.planId, mode);
      Taro.showToast({ title: '模式已更新', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '更新失败', icon: 'error' });
    }
  };

  const getDaysRemaining = () => {
    if (!currentPlan) return 0;
    const diff = new Date(currentPlan.examDate).getTime() - Date.now();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  // 按日期分组任务
  const groupedTasks = allTasks.reduce((acc, task) => {
    const date = task.taskDate;
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(task);
    return acc;
  }, {} as Record<string, Task[]>);

  const sortedDates = Object.keys(groupedTasks).sort((a, b) => new Date(a).getTime() - new Date(b).getTime());

  return (
    <View className='plan-detail-page'>
      {/* 计划概览 */}
      <View className='plan-overview'>
        <View className='overview-header'>
          <View className='exam-name'>{currentPlan?.examName}</View>
          <View className='exam-type'>{currentPlan?.examType}</View>
        </View>

        <View className='overview-stats'>
          <View className='stat-item'>
            <View className='stat-value'>{getDaysRemaining()}</View>
            <View className='stat-label'>距离考试</View>
          </View>
          <View className='stat-item'>
            <View className='stat-value'>{currentPlan?.totalTasks || 0}</View>
            <View className='stat-label'>总任务数</View>
          </View>
          <View className='stat-item'>
            <View className='stat-value'>{currentPlan?.completedTasks || 0}</View>
            <View className='stat-label'>已完成</View>
          </View>
          <View className='stat-item'>
            <View className='stat-value'>{Math.round((currentPlan?.completionRate || 0) * 100)}%</View>
            <View className='stat-label'>完成率</View>
          </View>
        </View>
      </View>

      {/* 监督模式设置 */}
      <View className='mode-section card'>
        <View className='section-title'>监督模式</View>
        <View className='mode-list'>
          {[
            { mode: SupervisionMode.Silent, name: '静默', desc: '不主动提醒' },
            { mode: SupervisionMode.Gentle, name: '温柔', desc: '每日定时提醒' },
            { mode: SupervisionMode.Intensive, name: '强化', desc: '多次督促' },
            { mode: SupervisionMode.TangSeng, name: '唐僧', desc: '持续唠叨' }
          ].map(item => (
            <View
              key={item.mode}
              className={`mode-item ${currentPlan?.currentMode === item.mode ? 'active' : ''}`}
              onClick={() => handleModeChange(item.mode)}
            >
              <View className='mode-info'>
                <View className='mode-name'>{item.name}</View>
                <View className='mode-desc'>{item.desc}</View>
              </View>
              {currentPlan?.currentMode === item.mode && (
                <View className='mode-check'>✓</View>
              )}
            </View>
          ))}
        </View>
      </View>

      {/* 任务列表 */}
      <View className='tasks-section card'>
        <View className='section-title'>任务日程</View>

        {sortedDates.length === 0 ? (
          <View className='empty-tasks'>暂无任务安排</View>
        ) : (
          <View className='task-dates'>
            {sortedDates.map(date => (
              <View key={date} className='date-group'>
                <View className='date-header'>
                  <View className='date-text'>{date}</View>
                  <View className='date-count'>
                    {groupedTasks[date].filter(t => t.status === TaskStatus.Completed).length}
                    /
                    {groupedTasks[date].length}
                  </View>
                </View>
                <View className='date-tasks'>
                  {groupedTasks[date].map(task => (
                    <View
                      key={task.taskId}
                      className={`task-item ${task.status === TaskStatus.Completed ? 'completed' : ''}`}
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
              </View>
            ))}
          </View>
        )}
      </View>

      {/* 操作按钮 */}
      <View className='actions'>
        <View
          className='action-btn primary'
          onClick={() => Taro.navigateTo({ url: `/pages/task/index?planId=${planId}` })}
        >
          查看今日任务
        </View>
        <View
          className='action-btn secondary'
          onClick={() => Taro.navigateTo({ url: `/pages/checkin/index?planId=${planId}` })}
        >
          今日打卡
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '计划详情'
});