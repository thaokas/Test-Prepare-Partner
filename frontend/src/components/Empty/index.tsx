import { View, Text } from '@tarojs/components';
import './index.scss';

interface EmptyProps {
  icon?: string;
  title?: string;
  description?: string;
  actionText?: string;
  onAction?: () => void;
}

export default function Empty({
  icon = '📋',
  title = '暂无数据',
  description = '',
  actionText = '',
  onAction
}: EmptyProps) {
  return (
    <View className='empty-component'>
      <Text className='empty-icon'>{icon}</Text>
      <Text className='empty-title'>{title}</Text>
      {description && <Text className='empty-desc'>{description}</Text>}
      {actionText && (
        <View className='empty-action' onClick={onAction}>
          {actionText}
        </View>
      )}
    </View>
  );
}