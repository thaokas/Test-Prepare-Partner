-- PrepKeeper 数据库初始化脚本
-- 执行此文件可一次性创建表结构并插入模拟数据

-- 导入表结构
\i ./schema.sql

-- 导入模拟数据
\i ./seed_data.sql

-- 验证数据
SELECT 'users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'study_plans', COUNT(*) FROM study_plans
UNION ALL
SELECT 'tasks', COUNT(*) FROM tasks
UNION ALL
SELECT 'checkins', COUNT(*) FROM checkins
UNION ALL
SELECT 'reminders', COUNT(*) FROM reminders
UNION ALL
SELECT 'easter_eggs', COUNT(*) FROM easter_eggs;