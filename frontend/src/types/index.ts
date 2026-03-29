// 用户相关类型
export interface User {
  userId: string;
  nickname: string;
  email: string;
  avatarUrl?: string;
  totalCheckins: number;
  currentStreak: number;
  maxStreak: number;
  createdAt: string;
}

// 计划相关类型
export interface StudyPlan {
  planId: string;
  userId: string;
  examName: string;
  examType: string;
  examDate: string;
  dailyHours: number;
  foundationLevel: number;
  weakSubjects?: string[];
  currentMode: SupervisionMode;
  planStatus: PlanStatus;
  currentPhase: StudyPhase;
  createdAt: string;
  totalTasks: number;
  completedTasks: number;
  completionRate: number;
}

// 监督模式枚举
export enum SupervisionMode {
  Silent = 0,    // 静默
  Gentle = 1,    // 温柔
  Intensive = 2, // 强化
  TangSeng = 3   // 唐僧
}

// 计划状态枚举
export enum PlanStatus {
  InProgress = 0, // 进行中
  Completed = 1,  // 已完成
  Paused = 2      // 已暂停
}

// 学习阶段枚举
export enum StudyPhase {
  Foundation = 1, // 基础阶段
  Enhancement = 2, // 强化阶段
  Sprint = 3      // 冲刺阶段
}

// 任务类型枚举
export enum TaskType {
  Study = 1,    // 学习
  Review = 2,   // 复习
  Practice = 3, // 刷题
  MockExam = 4  // 模考
}

// 任务状态枚举
export enum TaskStatus {
  NotStarted = 0, // 未开始
  InProgress = 1, // 进行中
  Completed = 2,  // 已完成
  Skipped = 3     // 已跳过
}

// 任务相关类型
export interface Task {
  taskId: string;
  planId: string;
  taskDate: string;
  subject: string;
  taskContent: string;
  estimatedMinutes?: number;
  taskType: TaskType;
  phase: StudyPhase;
  status: TaskStatus;
  completedAt?: string;
  checkinType?: number;
}

// 打卡相关类型
export interface Checkin {
  checkinId: string;
  userId: string;
  planId: string;
  checkinDate: string;
  completedTasks: number;
  totalTasks: number;
  completionRate: number;
  isMakeup: boolean;
  streakBroken: boolean;
  createdAt: string;
}

// 提醒相关类型
export interface Reminder {
  reminderId: string;
  userId: string;
  planId: string;
  reminderType: ReminderType;
  triggerTime: string;
  content?: string;
  isSent: boolean;
  sentAt?: string;
}

// 提醒类型枚举
export enum ReminderType {
  Daily = 1,    // 每日提醒
  Urgent = 2,   // 催更提醒
  Weekly = 3    // 周报提醒
}

// 彩蛋相关类型
export interface EasterEgg {
  recordId: string;
  userId: string;
  eggType: EasterEggType;
  triggerDate: string;
  content?: string;
  isTriggered: boolean;
}

// 彩蛋类型枚举
export enum EasterEggType {
  LateNight = 'late_night',
  Weekend = 'weekend',
  EarlyBird = 'early_bird',
  Random = 'random'
}

// API响应包装类型
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 认证响应类型
export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  user: User;
}

// 请求类型
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  nickname?: string;
}

export interface PlanCreateRequest {
  examName: string;
  examType: string;
  examDate: string;
  dailyHours: number;
  foundationLevel: number;
  weakSubjects?: string[];
  currentMode: SupervisionMode;
}

export interface CheckinRequest {
  planId: string;
  checkinType: number;
  content?: string;
  imageUrl?: string;
}

export interface ReminderConfigRequest {
  planId: string;
  reminderEnabled: boolean;
  reminderTime?: string;
  reminderType?: ReminderType;
}