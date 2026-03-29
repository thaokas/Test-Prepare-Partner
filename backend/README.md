# ECNU备考搭子 - Spring Boot后端

## 项目简介

ECNU备考搭子后端服务，基于Spring Boot 3.2构建，提供用户认证、计划管理、任务管理、打卡记录、定时提醒等功能。

## 技术栈

- Java 17
- Spring Boot 3.2.5
- Spring Data JPA
- Spring Security + JWT
- PostgreSQL
- SpringDoc OpenAPI

## 快速开始

### 环境要求

- JDK 17+
- Maven 3.8+
- PostgreSQL 14+

### 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE prepkeeper;
```

2. 修改 `application.yml` 中的数据库连接信息

### 运行项目

```bash
# 编译
mvn clean package -DskipTests

# 运行
java -jar target/prep-keeper-backend-1.0.0-SNAPSHOT.jar
```

### API文档

启动后访问：http://localhost:8080/swagger-ui.html

## 项目结构

```
src/main/java/com/prepkeeper/
├── config/          # 配置类
├── controller/      # 控制器
├── service/         # 服务层
│   └── scheduler/   # 定时任务
├── repository/      # 数据访问层
├── entity/          # 实体类
├── dto/             # 数据传输对象
├── security/        # 安全相关
├── exception/       # 异常处理
└── util/            # 工具类
```

## API接口

### 认证模块
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/refresh - 刷新Token
- GET /api/auth/me - 获取当前用户

### 用户模块
- GET /api/users/{userId} - 获取用户信息
- PUT /api/users/{userId} - 更新用户信息

### 计划模块
- POST /api/plans - 创建计划
- GET /api/plans/{planId} - 获取计划详情
- GET /api/plans/user/{userId} - 获取用户计划列表
- PUT /api/plans/{planId}/mode - 切换监督模式
- DELETE /api/plans/{planId} - 删除计划

### 任务模块
- GET /api/tasks/today - 获取今日任务
- PUT /api/tasks/{taskId}/status - 更新任务状态
- POST /api/tasks/{taskId}/complete - 完成任务

### 打卡模块
- POST /api/checkins - 提交打卡
- GET /api/checkins/history - 获取打卡历史

### 提醒模块
- PUT /api/reminders/config - 配置提醒

### Agent代理
- POST /api/agent/chat - 对话
- GET /api/agent/report/weekly - 获取周报

## 定时任务

- 每日提醒：根据用户设置的监督模式，在指定时间发送提醒
- 周报生成：每周日22:00自动生成周报
- 连续打卡检查：每天00:05检查昨日打卡情况，重置连续天数

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DB_USERNAME | 数据库用户名 | postgres |
| DB_PASSWORD | 数据库密码 | postgres |
| JWT_SECRET | JWT密钥 | (内置密钥) |
| AGENT_URL | Agent服务地址 | http://localhost:8000 |

## 与Agent服务交互

后端通过HTTP调用Python Agent服务：
- 计划生成：POST /api/plan/generate
- 打卡处理：POST /api/checkin
- 对话接口：POST /api/chat
- 周报生成：GET /api/report/weekly
- 提醒触发：POST /api/reminder/trigger