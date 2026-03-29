-- PrepKeeper Database Schema
-- PostgreSQL

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(64) PRIMARY KEY,
    nickname VARCHAR(50),
    password VARCHAR(256),
    email VARCHAR(100) UNIQUE,
    avatar_url VARCHAR(500),
    total_checkins INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    max_streak INTEGER DEFAULT 0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 备考计划表
CREATE TABLE IF NOT EXISTS study_plans (
    plan_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    exam_name VARCHAR(100) NOT NULL,
    exam_type VARCHAR(64) NOT NULL,
    exam_date DATE NOT NULL,
    daily_hours DECIMAL(3,1),
    foundation_level INTEGER DEFAULT 1,
    weak_subjects VARCHAR(500),
    current_mode INTEGER DEFAULT 1,          -- 监督模式: 0-静默 1-温柔 2-强化 3-唐僧
    plan_status INTEGER DEFAULT 0,           -- 计划状态: 0-进行中 1-已完成 2-已暂停
    current_phase INTEGER DEFAULT 1,         -- 当前阶段: 1-基础 2-强化 3-冲刺
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    CONSTRAINT fk_study_plans_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(64) PRIMARY KEY,
    plan_id VARCHAR(64) NOT NULL,
    task_date DATE NOT NULL,
    subject VARCHAR(50) NOT NULL,
    task_content VARCHAR(500) NOT NULL,
    estimated_minutes INTEGER,
    task_type INTEGER DEFAULT 1,             -- 任务类型: 1-学习 2-复习 3-刷题 4-模考
    phase INTEGER NOT NULL,                  -- 所属阶段: 1-基础 2-强化 3-冲刺
    status INTEGER DEFAULT 0,                -- 状态: 0-未开始 1-进行中 2-已完成 3-已跳过
    completed_at TIMESTAMP,
    checkin_type INTEGER,                    -- 打卡方式: 1-文字 2-图片
    created_at TIMESTAMP,
    CONSTRAINT fk_tasks_plan FOREIGN KEY (plan_id) REFERENCES study_plans(plan_id) ON DELETE CASCADE
);

-- 打卡记录表
CREATE TABLE IF NOT EXISTS checkins (
    checkin_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    plan_id VARCHAR(64) NOT NULL,
    checkin_date DATE NOT NULL,
    completed_tasks INTEGER DEFAULT 0,
    total_tasks INTEGER DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0,
    is_makeup INTEGER DEFAULT 0,             -- 是否为补卡: 0-否 1-是
    streak_broken INTEGER DEFAULT 0,         -- 是否中断连续: 0-否 1-是
    created_at TIMESTAMP,
    CONSTRAINT fk_checkins_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_checkins_plan FOREIGN KEY (plan_id) REFERENCES study_plans(plan_id) ON DELETE CASCADE
);

-- 提醒记录表
CREATE TABLE IF NOT EXISTS reminders (
    reminder_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    plan_id VARCHAR(64) NOT NULL,
    reminder_type INTEGER NOT NULL,          -- 提醒类型: 1-每日提醒 2-催更提醒 3-周报提醒
    trigger_time TIMESTAMP NOT NULL,
    content VARCHAR(1000),
    is_sent INTEGER DEFAULT 0,               -- 是否已发送: 0-否 1-是
    sent_at TIMESTAMP,
    CONSTRAINT fk_reminders_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_reminders_plan FOREIGN KEY (plan_id) REFERENCES study_plans(plan_id) ON DELETE CASCADE
);

-- 彩蛋触发记录表
CREATE TABLE IF NOT EXISTS easter_eggs (
    record_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    egg_type VARCHAR(50) NOT NULL,           -- 彩蛋类型: late_night/weekend/early_bird/random
    trigger_date DATE NOT NULL,
    content VARCHAR(500),
    is_triggered INTEGER DEFAULT 0,          -- 是否已触发: 0-否 1-是
    CONSTRAINT fk_easter_eggs_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_study_plans_user ON study_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_plan ON tasks(plan_id);
CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(task_date);
CREATE INDEX IF NOT EXISTS idx_checkins_user ON checkins(user_id);
CREATE INDEX IF NOT EXISTS idx_checkins_plan ON checkins(plan_id);
CREATE INDEX IF NOT EXISTS idx_checkins_date ON checkins(checkin_date);
CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id);
CREATE INDEX IF NOT EXISTS idx_reminders_plan ON reminders(plan_id);
CREATE INDEX IF NOT EXISTS idx_easter_eggs_user ON easter_eggs(user_id);