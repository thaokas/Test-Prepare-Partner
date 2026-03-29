import { View, Input, Button, Picker } from '@tarojs/components';
import Taro from '@tarojs/taro';
import { useState } from 'react';
import { useUserStore } from '@/store/user';
import { usePlanStore } from '@/store/plan';
import { SupervisionMode } from '@/types';
import './index.scss';

export default function CreatePlanPage() {
  const { user } = useUserStore();
  const { createPlan, isLoading } = usePlanStore();

  const [examName, setExamName] = useState('');
  const [examType, setExamType] = useState('');
  const [examDate, setExamDate] = useState('');
  const [dailyHours, setDailyHours] = useState('2');
  const [foundationLevel, setFoundationLevel] = useState(1);
  const [weakSubjects, setWeakSubjects] = useState('');
  const [supervisionMode, setSupervisionMode] = useState(SupervisionMode.Gentle);

  const examTypeOptions = ['考研', '公务员', '教师资格证', '英语四六级', '雅思托福', '注会', '司法考试', '其他'];
  const foundationOptions = ['零基础', '有一定基础', '已复习一轮'];
  const modeOptions = ['静默模式', '温柔提醒', '强化督促', '唐僧模式'];

  const handleExamTypeChange = (e) => {
    setExamType(examTypeOptions[e.detail.value]);
  };

  const handleFoundationChange = (e) => {
    setFoundationLevel(Number(e.detail.value));
  };

  const handleModeChange = (e) => {
    setSupervisionMode(Number(e.detail.value));
  };

  const handleDateChange = (e) => {
    setExamDate(e.detail.value);
  };

  const handleCreate = async () => {
    if (!examName || !examType || !examDate) {
      Taro.showToast({ title: '请填写必填信息', icon: 'error' });
      return;
    }

    try {
      await createPlan({
        examName,
        examType,
        examDate,
        dailyHours: Number(dailyHours),
        foundationLevel,
        weakSubjects: weakSubjects ? weakSubjects.split(',').map(s => s.trim()) : undefined,
        currentMode: supervisionMode
      });

      Taro.showToast({ title: '计划创建成功', icon: 'success' });
      Taro.navigateBack();
    } catch (error: any) {
      Taro.showToast({ title: error.message || '创建失败', icon: 'error' });
    }
  };

  return (
    <View className='create-plan-page'>
      <View className='form-section'>
        <View className='section-title'>考试信息</View>

        <View className='form-item'>
          <View className='label'>考试名称 *</View>
          <Input
            className='input'
            placeholder='如：2026年考研'
            value={examName}
            onInput={(e) => setExamName(e.detail.value)}
          />
        </View>

        <View className='form-item'>
          <View className='label'>考试类型 *</View>
          <Picker
            mode='selector'
            range={examTypeOptions}
            onChange={handleExamTypeChange}
          >
            <View className='picker-value'>
              {examType || '请选择考试类型'}
            </View>
          </Picker>
        </View>

        <View className='form-item'>
          <View className='label'>考试日期 *</View>
          <Picker
            mode='date'
            start={new Date().toISOString().split('T')[0]}
            onChange={handleDateChange}
          >
            <View className='picker-value'>
              {examDate || '请选择考试日期'}
            </View>
          </Picker>
        </View>
      </View>

      <View className='form-section'>
        <View className='section-title'>学习设置</View>

        <View className='form-item'>
          <View className='label'>每日学习时长（小时）</View>
          <Input
            className='input'
            type='number'
            placeholder='2'
            value={dailyHours}
            onInput={(e) => setDailyHours(e.detail.value)}
          />
        </View>

        <View className='form-item'>
          <View className='label'>基础水平</View>
          <Picker
            mode='selector'
            range={foundationOptions}
            value={foundationLevel}
            onChange={handleFoundationChange}
          >
            <View className='picker-value'>
              {foundationOptions[foundationLevel]}
            </View>
          </Picker>
        </View>

        <View className='form-item'>
          <View className='label'>薄弱科目（逗号分隔）</View>
          <Input
            className='input'
            placeholder='如：数学,英语'
            value={weakSubjects}
            onInput={(e) => setWeakSubjects(e.detail.value)}
          />
        </View>
      </View>

      <View className='form-section'>
        <View className='section-title'>监督模式</View>

        <View className='mode-options'>
          {modeOptions.map((mode, index) => (
            <View
              key={index}
              className={`mode-option ${supervisionMode === index ? 'active' : ''}`}
              onClick={() => setSupervisionMode(index)}
            >
              <View className='mode-name'>{mode}</View>
              <View className='mode-desc'>
                {index === 0 && '不主动发送提醒'}
                {index === 1 && '每日定时提醒'}
                {index === 2 && '多次提醒督促'}
                {index === 3 && '唠叨模式，持续督促'}
              </View>
            </View>
          ))}
        </View>
      </View>

      <Button
        className='submit-btn'
        loading={isLoading}
        onClick={handleCreate}
      >
        创建计划
      </Button>
    </View>
  );
}

definePageConfig({
  navigationBarTitleText: '创建计划'
});