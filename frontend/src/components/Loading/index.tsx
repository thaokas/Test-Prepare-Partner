import { View, Text } from '@tarojs/components';
import { PropsWithChildren } from 'react';
import './index.scss';

interface LoadingProps {
  text?: string;
}

export default function Loading({ text = '加载中...' }: PropsWithChildren<LoadingProps>) {
  return (
    <View className='loading-component'>
      <View className='loading-spinner'></View>
      <Text className='loading-text'>{text}</Text>
    </View>
  );
}