import { View, Text, Input, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect, useState } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { useTaskStore } from '@/store/task';
import { TaskStatus } from '@/types';
import './index.scss';

export default function CheckinPage() {
  const { user } = useUserStore();
  const { currentPlan, plans } = usePlanStore();
  const { todayTasks, fetchTodayTasks, completeTask, submitCheckin, currentStreak } = useTaskStore();

  const [selectedTasks, setSelectedTasks] = useState<string[]>([]);
  const [checkinContent, setCheckinContent] = useState('');
  const [planId, setPlanId] = useState('');

  useEffect(() => {
    const id = Taro.getCurrentInstance().router?.params?.planId || currentPlan?.planId;
    if (id) {
      setPlanId(id);
      fetchTodayTasks(id);
    }
  }, [currentPlan]);

  const handleTaskSelect = (taskId: string) => {
    setSelectedTasks(prev =>
      prev.includes(taskId)
        ? prev.filter(id => id !== taskId)
        : [...prev, taskId]
    );
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      await completeTask(taskId);
      if (!selectedTasks.includes(taskId)) {
        setSelectedTasks(prev => [...prev, taskId]);
      }
      Taro.showToast({ title: '任务完成', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '操作失败', icon: 'error' });
    }
  };

  const handleSubmitCheckin = async () => {
    if (selectedTasks.length === 0) {
      Taro.showToast({ title: '请选择完成的任务', icon: 'error' });
      return;
    }

    try {
      await submitCheckin(planId, 1, checkinContent);
      Taro.showToast({ title: '打卡成功', icon: 'success' });
      setCheckinContent('');
      setSelectedTasks([]);
    } catch (error: any) {
      Taro.showToast({ title: error.message || '打卡失败', icon: 'error' });
    }
  };

  const completedCount = todayTasks.filter(t => t.status === TaskStatus.Completed).length;
  const totalCount = todayTasks.length;

  return (
    <View className='checkin-page'>
      {/* 打卡统计 */}
      <View className='streak-banner'>
        <View className='streak-info'>
          <View className='streak-icon'>🔥</View>
          <View className='streak-text'>
            <View className='streak-value'>{currentStreak}</View>
            <View className='streak-label'>连续打卡天数</View>
          </View>
        </View>
        <View className='streak-motivation'>
          {currentStreak >= 7 ? '太棒了！坚持就是胜利！' : '继续加油，争取更多连续天数！'}
        </View>
      </View>

      {/* 今日任务完成情况 */}
      <View className='task-section card'>
        <View className='section-header'>
          <View className='section-title'>今日任务</View>
          <View className='completion-rate'>
            {completedCount}/{totalCount} 完成
          </View>
        </View>

        {todayTasks.length === 0 ? (
          <View className='no-tasks'>今日暂无任务安排</View>
        ) : (
          <View className='task-list'>
            {todayTasks.map(task => (
              <View
                key={task.taskId}
                className={`task-item ${task.status === TaskStatus.Completed ? 'completed' : ''} ${selectedTasks.includes(task.taskId) ? 'selected' : ''}`}
              >
                <View
                  className='task-checkbox'
                  onClick={() => handleTaskSelect(task.taskId)}
                >
                  {selectedTasks.includes(task.taskId) || task.status === TaskStatus.Completed ? '✓' : ''}
                </View>
                <View className='task-content'>
                  <View className='task-subject'>{task.subject}</View>
                  <View className='task-text'>{task.taskContent}</View>
                  <View className='task-meta'>
                    <Text className='task-time'>{task.estimatedMinutes}分钟</Text>
                  </View>
                </View>
                {task.status !== TaskStatus.Completed && (
                  <View
                    className='complete-btn'
                    onClick={() => handleCompleteTask(task.taskId)}
                  >
                    完成
                  </View>
                )}
              </View>
            ))}
          </View>
        )}
      </View>

      {/* 打卡心得 */}
      <View className='content-section card'>
        <View className='section-title'>打卡心得</View>
        <Input
          className='content-input'
          placeholder='写下今天的学习心得（可选）'
          value={checkinContent}
          onInput={(e) => setCheckinContent(e.detail.value)}
        />
      </View>

      {/* 提交打卡 */}
      <View className='submit-section'>
        <View className='selected-count'>
          已选择 {selectedTasks.length} 个任务
        </View>
        <Button
          className='submit-btn'
          onClick={handleSubmitCheckin}
          disabled={selectedTasks.length === 0}
        >
          提交打卡
        </Button>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '今日打卡'
});