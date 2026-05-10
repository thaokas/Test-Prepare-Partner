# 小搭 - Spring Boot后端开发计划

## 1. 架构定位

### 1.1 职责划分

```
┌──────────────────────────────────────────────────────────────────┐
│                         前端 (Web/移动端)                          │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Spring Boot 后端 (本项目)                        │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐        │
│  │ 用户认证模块    │ │ 业务数据管理    │ │ 定时任务调度   │        │
│  └────────────────┘ └────────────────┘ └────────────────┘        │
└─────────────────────────────┬────────────────────────────────────┘
                              │ HTTP
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Agent Service (Python/FastAPI)                  │
│           AI对话、计划生成、RAG检索、智能提醒                       │
└─────────────────────────────┬────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       PostgreSQL 数据库                           │
└──────────────────────────────────────────────────────────────────┘
```

### 1.2 Spring Boot 核心职责

| 模块 | 职责 | 说明 |
|------|------|------|
| 用户认证 | 注册、登录、JWT令牌管理 | 用户身份验证与授权 |
| 用户管理 | 用户信息CRUD、统计更新 | 用户基础数据维护 |
| 计划管理 | 计划创建/查询/修改/删除 | 调用Agent生成计划 |
| 任务管理 | 任务查询、状态更新 | 打卡相关业务 |
| 打卡管理 | 打卡记录、连续天数计算 | 与Agent协同处理 |
| 提醒管理 | 提醒配置、发送记录 | 定时任务触发 |
| Agent通信 | HTTP调用Agent服务 | 智能功能代理 |
| 定时任务 | 每日提醒、周报触发、连续检查 | Spring Scheduler |

### 1.3 技术栈

- **框架**: Spring Boot 3.2.x
- **Java版本**: JDK 17+
- **构建工具**: Maven
- **ORM**: Spring Data JPA + Hibernate
- **数据库**: PostgreSQL
- **认证**: Spring Security + JWT
- **API文档**: SpringDoc OpenAPI (Swagger)
- **定时任务**: Spring Scheduler
- **工具库**: Lombok, MapStruct, Hutool

---

## 2. 项目结构

```
backend/
├── pom.xml
├── src/main/java/com/prepkeeper/
│   ├── PrepKeeperApplication.java
│   ├── config/
│   │   ├── SecurityConfig.java          # Spring Security配置
│   │   ├── JwtConfig.java               # JWT配置
│   │   ├── SchedulerConfig.java         # 定时任务配置
│   │   ├── CorsConfig.java              # CORS配置
│   │   └── OpenApiConfig.java           # Swagger配置
│   ├── controller/
│   │   ├── AuthController.java          # 认证接口
│   │   ├── UserController.java          # 用户管理
│   │   ├── PlanController.java          # 计划管理
│   │   ├── TaskController.java          # 任务管理
│   │   ├── CheckinController.java       # 打卡管理
│   │   ├── ReminderController.java      # 提醒管理
│   │   └── AgentProxyController.java    # Agent代理接口
│   ├── service/
│   │   ├── AuthService.java
│   │   ├── UserService.java
│   │   ├── PlanService.java
│   │   ├── TaskService.java
│   │   ├── CheckinService.java
│   │   ├── ReminderService.java
│   │   ├── AgentClientService.java      # Agent服务调用
│   │   └── scheduler/
│   │       ├── DailyReminderScheduler.java
│   │       ├── WeeklyReportScheduler.java
│   │       └── StreakCheckScheduler.java
│   ├── repository/
│   │   ├── UserRepository.java
│   │   ├── StudyPlanRepository.java
│   │   ├── TaskRepository.java
│   │   ├── CheckinRepository.java
│   │   ├── ReminderRepository.java
│   │   └── EasterEggRepository.java
│   ├── entity/
│   │   ├── User.java
│   │   ├── StudyPlan.java
│   │   ├── Task.java
│   │   ├── Checkin.java
│   │   ├── Reminder.java
│   │   └── EasterEgg.java
│   ├── dto/
│   │   ├── request/
│   │   │   ├── LoginRequest.java
│   │   │   ├── RegisterRequest.java
│   │   │   ├── PlanCreateRequest.java
│   │   │   ├── CheckinRequest.java
│   │   │   └── ReminderConfigRequest.java
│   │   └── response/
│   │       ├── UserResponse.java
│   │       ├── PlanResponse.java
│   │       ├── TaskResponse.java
│   │       ├── CheckinResponse.java
│   │       └── ApiResponse.java
│   ├── security/
│   │   ├── JwtTokenProvider.java
│   │   ├── JwtAuthenticationFilter.java
│   │   └── UserPrincipal.java
│   ├── exception/
│   │   ├── GlobalExceptionHandler.java
│   │   ├── BusinessException.java
│   │   └── ErrorCode.java
│   └── util/
│       ├── IdGenerator.java
│       └── DateUtils.java
├── src/main/resources/
│   ├── application.yml
│   ├── application-dev.yml
│   ├── application-prod.yml
│   └── db/migration/                      # Flyway迁移脚本(可选)
├── src/test/java/com/prepkeeper/
│   └── ...测试类
└── README.md
```

---

## 3. API设计

### 3.1 认证模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/auth/register | 用户注册 | 否 |
| POST | /api/auth/login | 用户登录 | 否 |
| POST | /api/auth/refresh | 刷新Token | 否 |
| GET | /api/auth/me | 获取当前用户 | 是 |

### 3.2 用户模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/users/{userId} | 获取用户信息 | 是 |
| PUT | /api/users/{userId} | 更新用户信息 | 是 |
| GET | /api/users/{userId}/stats | 获取用户统计 | 是 |

### 3.3 计划模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/plans | 创建计划(调用Agent) | 是 |
| GET | /api/plans/{planId} | 获取计划详情 | 是 |
| GET | /api/plans/user/{userId} | 获取用户计划列表 | 是 |
| PUT | /api/plans/{planId} | 更新计划 | 是 |
| PUT | /api/plans/{planId}/mode | 切换监督模式 | 是 |
| DELETE | /api/plans/{planId} | 删除计划 | 是 |

### 3.4 任务模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/tasks/today | 获取今日任务 | 是 |
| GET | /api/tasks/plan/{planId} | 获取计划下所有任务 | 是 |
| PUT | /api/tasks/{taskId}/status | 更新任务状态 | 是 |
| POST | /api/tasks/{taskId}/complete | 完成单个任务 | 是 |

### 3.5 打卡模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/checkins | 提交打卡(调用Agent) | 是 |
| GET | /api/checkins/today | 获取今日打卡记录 | 是 |
| GET | /api/checkins/history | 获取打卡历史 | 是 |
| GET | /api/checkins/streak | 获取连续打卡天数 | 是 |

### 3.6 提醒模块

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | /api/reminders | 获取提醒列表 | 是 |
| PUT | /api/reminders/config | 配置提醒设置 | 是 |
| GET | /api/reminders/history | 获取提醒历史 | 是 |

### 3.7 Agent代理接口

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | /api/agent/chat | 对话代理 | 是 |
| POST | /api/agent/generate-plan | 计划生成代理 | 是 |
| GET | /api/agent/report/weekly | 周报代理 | 是 |

---

## 4. 定时任务设计

### 4.1 每日提醒任务

```java
// Cron: 0 0 21-22 * * ? (根据用户模式触发)
// 逻辑:
// 1. 查询所有非静默模式的活跃计划
// 2. 根据模式筛选触发时间
// 3. 检查今日是否有未完成任务
// 4. 调用Agent生成提醒内容
// 5. 记录提醒发送状态
```

### 4.2 周报生成任务

```java
// Cron: 0 0 22 ? * SUN (每周日22:00)
// 逻辑:
// 1. 查询所有活跃用户
// 2. 调用Agent生成周报
// 3. 推送给用户
```

### 4.3 连续打卡检查任务

```java
// Cron: 0 0 0 * * ? (每天00:00)
// 逻辑:
// 1. 查询昨日未打卡的用户
// 2. 重置连续打卡天数为0
// 3. 可选: 发送关怀消息
```

---

## 5. Agent服务交互

### 5.1 配置

```yaml
agent:
  service:
    url: http://localhost:8000
    timeout: 30000
    retry: 3
```

### 5.2 调用示例

```java
@Service
public class AgentClientService {

    @Value("${agent.service.url}")
    private String agentUrl;

    private final RestTemplate restTemplate;

    // 对话接口
    public ChatResponse chat(String userId, String message) {
        ChatRequest request = new ChatRequest(userId, message);
        return restTemplate.postForObject(agentUrl + "/api/chat", request, ChatResponse.class);
    }

    // 计划生成
    public PlanGenerateResponse generatePlan(PlanGenerateRequest request) {
        return restTemplate.postForObject(agentUrl + "/api/plan/generate", request, PlanGenerateResponse.class);
    }

    // 打卡处理
    public CheckinResponse processCheckin(CheckinRequest request) {
        return restTemplate.postForObject(agentUrl + "/api/checkin", request, CheckinResponse.class);
    }
}
```

---

## 6. 开发阶段规划

### 阶段一: 基础框架搭建 (Day 1)

- [x] 创建Spring Boot项目
- [ ] 配置Maven依赖
- [ ] 配置数据库连接
- [ ] 创建实体类(Entity)
- [ ] 创建Repository层
- [ ] 配置Spring Security + JWT

### 阶段二: 核心业务开发 (Day 2-3)

- [ ] 用户注册/登录接口
- [ ] 用户信息管理
- [ ] 计划CRUD接口
- [ ] 任务查询接口
- [ ] 打卡接口
- [ ] Agent服务调用封装

### 阶段三: 定时任务与提醒 (Day 4)

- [ ] Spring Scheduler配置
- [ ] 每日提醒任务
- [ ] 周报生成任务
- [ ] 连续打卡检查任务

### 阶段四: 测试与文档 (Day 5)

- [ ] 单元测试
- [ ] 集成测试
- [ ] API文档完善
- [ ] 部署配置

---

## 7. 数据库配置

### application.yml

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:5432/prepkeeper
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:postgres}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
    properties:
      hibernate:
        format_sql: true
        dialect: org.hibernate.dialect.PostgreSQLDialect

server:
  port: 8080

jwt:
  secret: ${JWT_SECRET:your-secret-key-at-least-256-bits-long}
  expiration: 86400000  # 24小时

agent:
  service:
    url: ${AGENT_URL:http://localhost:8000}
    timeout: 30000
```

---

## 8. 安全设计

### 8.1 认证流程

```
1. 用户注册/登录 -> 返回JWT Token
2. 后续请求携带 Token -> Authorization: Bearer {token}
3. JwtAuthenticationFilter 验证Token
4. 验证通过 -> 获取用户信息 -> 继续请求
```

### 8.2 权限控制

- 用户只能访问自己的数据
- 管理员可以访问所有数据
- API接口根据角色控制访问

---

## 9. 错误处理

### 统一响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误码设计

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 用户不存在 |
| 1002 | 密码错误 |
| 1003 | 用户已存在 |
| 2001 | 计划不存在 |
| 2002 | 任务不存在 |
| 3001 | Token无效 |
| 3002 | Token过期 |
| 5001 | Agent服务异常 |
| 9999 | 系统异常 |

---

## 10. 后续优化方向

1. **缓存**: 引入Redis缓存用户信息、任务列表
2. **消息队列**: 打卡、提醒等异步处理
3. **日志**: ELK日志收集与分析
4. **监控**: Prometheus + Grafana监控
5. **容器化**: Docker部署配置
6. **CI/CD**: GitHub Actions自动化部署