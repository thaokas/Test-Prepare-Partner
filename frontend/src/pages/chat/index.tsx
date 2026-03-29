import { View, Text, Input, ScrollView } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState, useEffect, useRef } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { chatWithAgent, generatePlan, getWeeklyReport } from '@/services/agent';
import './index.scss';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  time: string;
}

export default function ChatPage() {
  const { user } = useUserStore();
  const { currentPlan } = usePlanStore();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'agent',
      content: '你好！我是你的备考AI助手。我可以帮你制定学习计划、解答备考问题、提供学习建议。有什么需要帮助的吗？',
      time: new Date().toLocaleTimeString()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollViewRef = useRef(null);

  const handleSend = async () => {
    if (!inputText.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputText,
      time: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await chatWithAgent(user?.userId || '', inputText);

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: response.response,
        time: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: '抱歉，我遇到了一些问题。请稍后再试。',
        time: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleQuickAction = async (action: string) => {
    setIsLoading(true);

    try {
      let response: any;

      if (action === 'weekly') {
        response = await getWeeklyReport(user?.userId || '');
        const agentMessage: Message = {
          id: Date.now().toString(),
          type: 'agent',
          content: `【本周周报】\n完成任务：${response.completedTasks}/${response.totalTasks}\n连续打卡：${response.streakDays}天\n\n${response.summary}`,
          time: new Date().toLocaleTimeString()
        };
        setMessages(prev => [...prev, agentMessage]);
      } else if (action === 'plan') {
        if (!currentPlan) {
          const agentMessage: Message = {
            id: Date.now().toString(),
            type: 'agent',
            content: '你还没有创建学习计划，请先创建一个计划吧！',
            time: new Date().toLocaleTimeString()
          };
          setMessages(prev => [...prev, agentMessage]);
        } else {
          const agentMessage: Message = {
            id: Date.now().toString(),
            type: 'agent',
            content: `当前计划：${currentPlan.examName}\n考试日期：${currentPlan.examDate}\n监督模式：${getModeText(currentPlan.currentMode)}\n完成进度：${Math.round(currentPlan.completionRate * 100)}%`,
            time: new Date().toLocaleTimeString()
          };
          setMessages(prev => [...prev, agentMessage]);
        }
      }
    } catch (error: any) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'agent',
        content: '抱歉，获取信息失败。',
        time: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const getModeText = (mode: number) => {
    const modes = ['静默', '温柔', '强化', '唐僧'];
    return modes[mode] || '未知';
  };

  return (
    <View className='chat-page'>
      {/* 快捷操作 */}
      <View className='quick-actions'>
        <View className='action-item' onClick={() => handleQuickAction('weekly')}>
          📊 周报分析
        </View>
        <View className='action-item' onClick={() => handleQuickAction('plan')}>
          📋 当前计划
        </View>
        <View className='action-item' onClick={() => setInputText('给我一些学习建议')}>
          💡 学习建议
        </View>
      </View>

      {/* 消息列表 */}
      <ScrollView
        className='message-list'
        scrollY
        scrollIntoView={messages.length > 0 ? `msg-${messages[messages.length - 1].id}` : ''}
      >
        {messages.map(msg => (
          <View key={msg.id} id={`msg-${msg.id}`} className={`message-item ${msg.type}`}>
            <View className='message-avatar'>
              {msg.type === 'user' ? '👤' : '🤖'}
            </View>
            <View className='message-content'>
              <View className='message-text'>{msg.content}</View>
              <View className='message-time'>{msg.time}</View>
            </View>
          </View>
        ))}

        {isLoading && (
          <View className='message-item agent'>
            <View className='message-avatar'>🤖</View>
            <View className='message-content loading'>
              正在思考中...
            </View>
          </View>
        )}
      </ScrollView>

      {/* 输入区域 */}
      <View className='input-area'>
        <Input
          className='message-input'
          placeholder='输入消息...'
          value={inputText}
          onInput={(e) => setInputText(e.detail.value)}
          onConfirm={handleSend}
        />
        <View
          className={`send-btn ${inputText.trim() ? 'active' : ''}`}
          onClick={handleSend}
        >
          发送
        </View>
      </View>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: 'AI助手'
});