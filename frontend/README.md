# ECNU备考搭子 - Taro前端

基于Taro框架开发的备考助手前端应用，支持微信小程序、H5等多端运行。

## 项目简介

ECNU备考搭子是一款智能备考助手应用，提供学习计划管理、每日任务打卡、AI助手对话等功能，帮助用户高效备考。

## 技术栈

- **框架**: Taro 3.6.x
- **语言**: TypeScript
- **UI**: 自定义组件 + Sass
- **状态管理**: Zustand
- **构建工具**: Webpack 5
- **包管理**: pnpm

## 项目结构

```
frontend/
├── config/                # Taro配置文件
│   ├── index.ts          # 主配置
│   ├── dev.ts            # 开发环境配置
│   └── prod.ts           # 生产环境配置
├── src/
│   ├── app.tsx           # 应用入口
│   ├── app.config.ts     # 应用配置（页面路由、tabBar等）
│   ├── app.scss          # 全局样式
│   ├── index.html        # H5入口HTML
│   ├── components/       # 通用组件
│   │   ├── Loading/      # 加载组件
│   │   ├── Empty/        # 空状态组件
│   │   └── ProgressBar/  # 进度条组件
│   ├── pages/            # 页面组件
│   │   ├── login/        # 登录页
│   │   ├── register/     # 注册页
│   │   ├── home/         # 首页
│   │   ├── plan/         # 计划列表
│   │   │   ├── create/   # 创建计划
│   │   │   └── detail/   # 计划详情
│   │   ├── task/         # 任务列表
│   │   ├── checkin/      # 打卡页
│   │   ├── profile/      # 个人中心
│   │   └── chat/         # AI助手对话
│   ├── services/         # API服务层
│   │   ├── auth.ts       # 认证API
│   │   ├── plan.ts       # 计划API
│   │   ├── task.ts       # 任务API
│   │   ├── checkin.ts    # 打卡API
│   │   ├── reminder.ts   # 提醒API
│   │   └── agent.ts      # Agent API
│   ├── store/            # 状态管理
│   │   ├── user.ts       # 用户状态
│   │   ├── plan.ts       # 计划状态
│   │   └── task.ts       # 任务状态
│   ├── types/            # TypeScript类型定义
│   └── utils/            # 工具函数
│       └── request.ts    # 网络请求封装
├── package.json
├── tsconfig.json
└── project.config.json   # 微信小程序项目配置
```

## 功能模块

### 用户认证
- 用户注册/登录
- JWT Token管理
- 自动Token刷新

### 学习计划
- 创建学习计划（考试类型、日期、每日时长）
- 监督模式设置（静默/温柔/强化/唐僧）
- 计划进度查看
- 计划删除

### 任务管理
- 今日任务查看
- 任务完成/跳过操作
- 任务进度统计

### 打卡记录
- 每日打卡提交
- 连续打卡天数统计
- 打卡心得记录

### AI助手
- 对话交互
- 周报分析
- 学习建议

### 个人中心
- 用户信息展示
- 打卡统计
- 设置管理

## API对接

后端API地址配置在 `src/utils/request.ts` 中：

```typescript
const BASE_URL = 'http://localhost:8080/api';
```

主要API接口：

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | POST /api/auth/login | 用户登录 |
| 认证 | POST /api/auth/register | 用户注册 |
| 计划 | POST /api/plans | 创建计划 |
| 计划 | GET /api/plans/user/{userId} | 获取用户计划 |
| 任务 | GET /api/tasks/today | 获取今日任务 |
| 任务 | POST /api/tasks/{taskId}/complete | 完成任务 |
| 打卡 | POST /api/checkins | 提交打卡 |
| Agent | POST /api/agent/chat | AI对话 |

## 快速开始

### 安装 pnpm

```bash
# 如果未安装pnpm，先安装
npm install -g pnpm
```

### 安装依赖

```bash
cd frontend
pnpm install
```

### 开发模式

```bash
# 微信小程序
pnpm run dev:weapp

# H5
pnpm run dev:h5
```

### 生产构建

```bash
# 微信小程序
pnpm run build:weapp

# H5
pnpm run build:h5
```

## 微信小程序调试

1. 使用微信开发者工具打开项目
2. 导入 `frontend` 目录
3. AppID需要替换为实际的微信小程序AppID

## 注意事项

1. **网络请求**: 微信小程序需要在后台配置合法域名
2. **存储**: 使用Taro.storage进行本地存储，支持多端
3. **路由**: 页面路由使用Taro.navigateTo/redirectTo
4. **样式**: 使用Sass编写样式，支持rpx单位

## 后端项目

后端Spring Boot项目位于 `/backend` 目录，提供完整的API服务。

## License

MIT