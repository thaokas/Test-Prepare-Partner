import { View, Input, Button } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';
import { useUserStore } from '@/store/user';
import './index.scss';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const { register, isLoading } = useUserStore();

  const handleRegister = async () => {
    if (!email || !password) {
      Taro.showToast({ title: '请填写邮箱和密码', icon: 'error' });
      return;
    }

    if (password.length < 6) {
      Taro.showToast({ title: '密码至少6位', icon: 'error' });
      return;
    }

    try {
      await register(email, password, nickname);
      Taro.showToast({ title: '注册成功', icon: 'success' });
    } catch (error: any) {
      Taro.showToast({ title: error.message || '注册失败', icon: 'error' });
    }
  };

  const goToLogin = () => {
    Taro.navigateBack();
  };

  return (
    <View className='register-page'>
      <View className='register-header'>
        <View className='title'>创建账号</View>
        <View className='subtitle'>开始你的备考之旅</View>
      </View>

      <View className='register-form'>
        <View className='form-item'>
          <View className='label'>昵称（可选）</View>
          <Input
            className='input'
            type='text'
            placeholder='给自己取个名字吧'
            value={nickname}
            onInput={(e) => setNickname(e.detail.value)}
          />
        </View>

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
            placeholder='至少6位密码'
            value={password}
            onInput={(e) => setPassword(e.detail.value)}
          />
        </View>

        <Button
          className='register-btn'
          loading={isLoading}
          onClick={handleRegister}
        >
          注册
        </Button>

        <View className='login-link' onClick={goToLogin}>
          已有账号？返回登录
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '注册'
});