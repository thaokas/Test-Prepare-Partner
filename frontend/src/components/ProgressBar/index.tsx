import { View, Text } from '@tarojs/components';
import './index.scss';

interface ProgressBarProps {
  percent: number;
  showText?: boolean;
  height?: number;
  color?: string;
}

export default function ProgressBar({
  percent,
  showText = true,
  height = 8,
  color = '#4A90D9'
}: ProgressBarProps) {
  return (
    <View className='progress-bar-component'>
      <View className='progress-bar' style={{ height: `${height}px` }}>
        <View
          className='progress-fill'
          style={{
            width: `${Math.min(100, Math.max(0, percent))}%`,
            background: color
          }}
        />
      </View>
      {showText && (
        <Text className='progress-text'>{Math.round(percent)}%</Text>
      )}
    </View>
  );
}