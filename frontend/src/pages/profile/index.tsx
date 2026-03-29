import { View, Text, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useEffect } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { useTaskStore } from '@/store/task';
import './index.scss';

export default function ProfilePage() {
  const { user, fetchCurrentUser, logout, isLoggedIn } = useUserStore();
  const { plans, fetchUserPlans } = usePlanStore();
  const { currentStreak, fetchCheckinStreak, checkinHistory, fetchCheckinHistory } = useTaskStore();

  useEffect(() => {
    if (!isLoggedIn) {
      Taro.redirectTo({ url: '/pages/login/index' });
      return;
    }
    if (!user) {
      fetchCurrentUser();
    }
    if (user && plans.length === 0) {
      fetchUserPlans(user.userId);
      fetchCheckinStreak();
      fetchCheckinHistory();
    }
  }, [isLoggedIn, user]);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('退出登录失败', error);
    }
  };

  const handleNavigate = (url: string) => {
    Taro.navigateTo({ url });
  };

  return (
    <View className='profile-page'>
      {/* 用户信息 */}
      <View className='user-info card'>
        <View className='avatar'>
          <Text className='avatar-text'>👤</Text>
        </View>
        <View className='info'>
          <View className='nickname'>{user?.nickname || '备考人'}</View>
          <View className='email'>{user?.email}</View>
        </View>
        <View className='edit-btn' onClick={() => handleNavigate('/pages/profile/edit')}>
          编辑
        </View>
      </View>

      {/* 打卡统计 */}
      <View className='stats-section'>
        <View className='stat-item'>
          <View className='stat-icon'>🔥</View>
          <View className='stat-value'>{currentStreak}</View>
          <View className='stat-label'>连续打卡</View>
        </View>
        <View className='stat-item'>
          <View className='stat-icon'>📊</View>
          <View className='stat-value'>{user?.totalCheckins || 0}</View>
          <View className='stat-label'>总打卡数</View>
        </View>
        <View className='stat-item'>
          <View className='stat-icon'>🏆</View>
          <View className='stat-value'>{user?.maxStreak || 0}</View>
          <View className='stat-label'>最长连续</View>
        </View>
        <View className='stat-item'>
          <View className='stat-icon'>📝</View>
          <View className='stat-value'>{plans.length}</View>
          <View className='stat-label'>计划数</View>
        </View>
      </View>

      {/* 功能菜单 */}
      <View className='menu-section card'>
        <View className='menu-item' onClick={() => handleNavigate('/pages/plan/index')}>
          <View className='menu-icon'>📋</View>
          <View className='menu-text'>我的计划</View>
          <View className='menu-arrow'>→</View>
        </View>

        <View className='menu-item' onClick={() => handleNavigate('/pages/checkin/history')}>
          <View className='menu-icon'>📅</View>
          <View className='menu-text'>打卡记录</View>
          <View className='menu-arrow'>→</View>
        </View>

        <View className='menu-item' onClick={() => handleNavigate('/pages/chat/index')}>
          <View className='menu-icon'>🤖</View>
          <View className='menu-text'>AI助手</View>
          <View className='menu-arrow'>→</View>
        </View>

        <View className='menu-item' onClick={() => handleNavigate('/pages/reminders/index')}>
          <View className='menu-icon'>🔔</View>
          <View className='menu-text'>提醒设置</View>
          <View className='menu-arrow'>→</View>
        </View>

        <View className='menu-item' onClick={() => handleNavigate('/pages/about/index')}>
          <View className='menu-icon'>ℹ️</View>
          <View className='menu-text'>关于我们</View>
          <View className='menu-arrow'>→</View>
        </View>
      </View>

      {/* 退出登录 */}
      <Button className='logout-btn' onClick={handleLogout}>
        退出登录
      </Button>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '我的'
});