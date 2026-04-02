import { View, Input, Button, Text } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';
import { useUserStore } from '@/store/user';
import './index.scss';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [focusedField, setFocusedField] = useState<string | null>(null);
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
      {/* Decorative background elements */}
      <View className='bg-decoration'>
        <View className='floating-shape shape-1' />
        <View className='floating-shape shape-2' />
        <View className='floating-shape shape-3' />
        <View className='grid-pattern' />
      </View>

      {/* Main content */}
      <View className='login-content'>
        {/* Header with animated logo */}
        <View className='login-header'>
          <View className='logo-wrapper'>
            <View className='logo-icon'>
              <Text className='logo-symbol'>☀</Text>
            </View>
            <Text className='logo-text'>备考搭子</Text>
          </View>
          <Text className='tagline'>专注每一个备考日夜，陪你抵达梦想彼岸</Text>
          <View className='header-accent' />
        </View>

        {/* Login form card */}
        <View className='login-card'>
          <View className='card-header'>
            <Text className='card-title'>欢迎回来</Text>
            <Text className='card-subtitle'>继续你的备考之旅</Text>
          </View>

          <View className='form-body'>
            {/* Email field */}
            <View className={`form-field ${focusedField === 'email' ? 'focused' : ''} ${email ? 'has-value' : ''}`}>
              <View className='field-icon'>
                <Text className='icon'>✉</Text>
              </View>
              <View className='field-content'>
                <Text className='floating-label'>邮箱地址</Text>
                <Input
                  className='field-input'
                  type='text'
                  placeholder=''
                  value={email}
                  onInput={(e) => setEmail(e.detail.value)}
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                />
              </View>
              <View className='field-line' />
            </View>

            {/* Password field */}
            <View className={`form-field ${focusedField === 'password' ? 'focused' : ''} ${password ? 'has-value' : ''}`}>
              <View className='field-icon'>
                <Text className='icon'>◈</Text>
              </View>
              <View className='field-content'>
                <Text className='floating-label'>密码</Text>
                <Input
                  className='field-input'
                  type='password'
                  placeholder=''
                  value={password}
                  onInput={(e) => setPassword(e.detail.value)}
                  onFocus={() => setFocusedField('password')}
                  onBlur={() => setFocusedField(null)}
                />
              </View>
              <View className='field-line' />
            </View>

            {/* Login button */}
            <Button
              className={`login-btn ${email && password ? 'active' : ''}`}
              loading={isLoading}
              onClick={handleLogin}
            >
              <Text className='btn-text'>登录</Text>
              <Text className='btn-arrow'>→</Text>
            </Button>

            {/* Divider */}
            <View className='divider'>
              <View className='divider-line' />
              <Text className='divider-text'>或</Text>
              <View className='divider-line' />
            </View>

            {/* Register link */}
            <View className='register-section'>
              <Text className='register-text'>还没有账号？</Text>
              <View className='register-link' onClick={goToRegister}>
                <Text className='link-text'>立即注册</Text>
                <View className='link-underline' />
              </View>
            </View>
          </View>
        </View>

        {/* Footer */}
        <View className='login-footer'>
          <Text className='footer-text'>ECNU 备考助手</Text>
          <View className='footer-dots'>
            <View className='dot' />
            <View className='dot' />
            <View className='dot' />
          </View>
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '',
  navigationBarBackgroundColor: '#0f1419',
  navigationBarTextStyle: 'white'
});