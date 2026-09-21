# 私人营养师系统 —— 数据库设计文档（精简版）

**版本**：v1.1  
**数据库**：MySQL 8.0  
**字符集**：utf8mb4

---

## 一、ER 关系概览

```
user 1──N food_record 1──N comment
                │
                ├──N like
                │
                └──N nutrition_daily（按天聚合）
```

- 一个用户有多条饮食记录
- 一条记录有多个点赞、多条评论
- 评论支持两层：一级评论 + 二级回复
- 每日营养聚合按用户+日期唯一

---

## 二、表结构

### 1. user（用户表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password | VARCHAR(100) | NOT NULL | 加密密码 |
| height | DECIMAL(5,2) | | 身高cm |
| weight | DECIMAL(5,2) | | 体重kg |
| age | INT | | 年龄 |
| gender | VARCHAR(10) | | 男/女 |
| goal | VARCHAR(20) | | 减脂/增肌/控糖/维持 |
| avoid | VARCHAR(200) | | 忌口 |
| allergy | VARCHAR(200) | | 过敏原 |
| avatar | VARCHAR(255) | | 头像 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | ON UPDATE | 更新时间 |

**索引**：`idx_username(username)`

---

### 2. food_record（饮食记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| user_id | BIGINT | FK, NOT NULL | 用户ID |
| food_name | VARCHAR(100) | NOT NULL | 食物名 |
| portion | VARCHAR(50) | | 份量 |
| meal_type | VARCHAR(20) | | 早/中/晚/加餐 |
| calories | DECIMAL(8,2) | | 热量 |
| protein | DECIMAL(8,2) | | 蛋白质 |
| fat | DECIMAL(8,2) | | 脂肪 |
| carbs | DECIMAL(8,2) | | 碳水 |
| fiber | DECIMAL(8,2) | | 纤维 |
| sodium | DECIMAL(8,2) | | 钠 |
| image_url | VARCHAR(255) | | 图片地址 |
| confidence | DECIMAL(5,2) | | 识别置信度 |
| is_corrected | TINYINT | DEFAULT 0 | 是否人工修正 |
| visibility | VARCHAR(10) | DEFAULT 'private' | public/private |
| record_date | DATE | NOT NULL | 记录日期 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

**索引**：
- `idx_user_date(user_id, record_date)`
- `idx_visibility(visibility, created_at)`

---

### 3. nutrition_daily（每日营养聚合表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| user_id | BIGINT | FK, NOT NULL | 用户ID |
| record_date | DATE | NOT NULL | 日期 |
| total_calories | DECIMAL(8,2) | | 总热量 |
| total_protein | DECIMAL(8,2) | | 总蛋白质 |
| total_fat | DECIMAL(8,2) | | 总脂肪 |
| total_carbs | DECIMAL(8,2) | | 总碳水 |
| total_fiber | DECIMAL(8,2) | | 总纤维 |
| total_sodium | DECIMAL(8,2) | | 总钠 |

**唯一索引**：`uk_user_date(user_id, record_date)`

---

### 4. like（点赞表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| user_id | BIGINT | FK, NOT NULL | 点赞用户 |
| record_id | BIGINT | FK, NOT NULL | 记录ID |
| created_at | DATETIME | DEFAULT NOW | 点赞时间 |

**唯一索引**：`uk_user_record(user_id, record_id)`（防重复点赞）  
**普通索引**：`idx_record(record_id)`

---

### 5. comment（评论表，支持分楼）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| record_id | BIGINT | FK, NOT NULL | 记录ID |
| user_id | BIGINT | FK, NOT NULL | 评论用户 |
| parent_id | BIGINT | DEFAULT NULL | 父评论ID，NULL=一级评论 |
| content | VARCHAR(500) | NOT NULL | 评论内容 |
| created_at | DATETIME | DEFAULT NOW | 评论时间 |

**索引**：
- `idx_record(record_id, created_at)`
- `idx_parent(parent_id)`

**分楼规则**：
- `parent_id = NULL`：一级评论
- `parent_id = 某条一级评论ID`：二级回复
- 最多两层，不允许回复二级评论

---

### 6. ai_log（AI调用日志表，可选）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | BIGINT | PK, AUTO | 主键 |
| user_id | BIGINT | | 用户ID |
| type | VARCHAR(20) | | recognize/advice/recipe |
| latency | INT | | 耗时ms |
| success | TINYINT | | 是否成功 |
| created_at | DATETIME | DEFAULT NOW | 调用时间 |

**索引**：`idx_user_type(user_id, type)`

---

## 三、建表 SQL

```sql
-- 用户表
CREATE TABLE user (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL,
  height DECIMAL(5,2),
  weight DECIMAL(5,2),
  age INT,
  gender VARCHAR(10),
  goal VARCHAR(20),
  avoid VARCHAR(200),
  allergy VARCHAR(200),
  avatar VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 饮食记录表
CREATE TABLE food_record (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  food_name VARCHAR(100) NOT NULL,
  portion VARCHAR(50),
  meal_type VARCHAR(20),
  calories DECIMAL(8,2),
  protein DECIMAL(8,2),
  fat DECIMAL(8,2),
  carbs DECIMAL(8,2),
  fiber DECIMAL(8,2),
  sodium DECIMAL(8,2),
  image_url VARCHAR(255),
  confidence DECIMAL(5,2),
  is_corrected TINYINT DEFAULT 0,
  visibility VARCHAR(10) DEFAULT 'private',
  record_date DATE NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_date (user_id, record_date),
  INDEX idx_visibility (visibility, created_at),
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 每日营养聚合表
CREATE TABLE nutrition_daily (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  record_date DATE NOT NULL,
  total_calories DECIMAL(8,2),
  total_protein DECIMAL(8,2),
  total_fat DECIMAL(8,2),
  total_carbs DECIMAL(8,2),
  total_fiber DECIMAL(8,2),
  total_sodium DECIMAL(8,2),
  UNIQUE KEY uk_user_date (user_id, record_date),
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 点赞表
CREATE TABLE `like` (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,
  record_id BIGINT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_user_record (user_id, record_id),
  INDEX idx_record (record_id),
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (record_id) REFERENCES food_record(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 评论表
CREATE TABLE comment (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  record_id BIGINT NOT NULL,
  user_id BIGINT NOT NULL,
  parent_id BIGINT DEFAULT NULL,
  content VARCHAR(500) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_record (record_id, created_at),
  INDEX idx_parent (parent_id),
  FOREIGN KEY (record_id) REFERENCES food_record(id),
  FOREIGN KEY (user_id) REFERENCES user(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- AI日志表（可选）
CREATE TABLE ai_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT,
  type VARCHAR(20),
  latency INT,
  success TINYINT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_type (user_id, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 四、关键设计说明

| 设计点 | 说明 |
|--------|------|
| 点赞防重 | `uk_user_record` 唯一索引 |
| 评论分楼 | `parent_id` 自关联，最多两层 |
| 公开广场 | `visibility + created_at` 联合索引 |
| 每日聚合 | `uk_user_date` 保证唯一 |
| 记录查询 | `user_id + record_date` 联合索引 |
| 密码 | 后端加密存储，不存明文 |
| 头像 | 存URL，不存二进制 |

---

## 五、表清单

| 表名 | 说明 | 必须 |
|------|------|------|
| user | 用户 | ✅ |
| food_record | 饮食记录 | ✅ |
| nutrition_daily | 每日聚合 | ✅ |
| like | 点赞 | ✅ |
| comment | 评论 | ✅ |
| ai_log | AI日志 | 可选 |
