import { View, Input, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';
import { useUserStore } from '@/store/user';
import './index.scss';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login, isLoading } = useUserStore();

  const handleLogin = async () => {
    if (!email || !password) {
      Taro.showToast({ title: '请填写邮箱和密码', icon: 'error' });
      return;
    }

    try {
      await login(email, password);
      Taro.showToast({ title: '登录成功', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '登录失败', icon: 'error' });
    }
  };

  const goToRegister = () => {
    Taro.navigateTo({ url: '/pages/register/index' });
  };

  return (
    <View className='login-page'>
      <View className='login-header'>
        <View className='logo'>备考搭子</View>
        <View className='subtitle'>ECNU备考助手，陪你一起上岸</View>
      </View>

      <View className='login-form'>
        <View className='form-item'>
          <View className='label'>邮箱</View>
          <Input
            className='input'
            type='text'
            placeholder='请输入邮箱'
            value={email}
            onInput={(e) => setEmail(e.detail.value)}
          />
        </View>

        <View className='form-item'>
          <View className='label'>密码</View>
          <Input
            className='input'
            type='password'
            placeholder='请输入密码'
            value={password}
            onInput={(e) => setPassword(e.detail.value)}
          />
        </View>

        <Button
          className='login-btn'
          loading={isLoading}
          onClick={handleLogin}
        >
          登录
        </Button>

        <View className='register-link' onClick={goToRegister}>
          没有账号？立即注册
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '登录'
});