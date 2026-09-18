# 私人营养师系统 —— 接口文档（精简版）

**版本**：v1.1  
**规范**：RESTful + JSON  
**统一响应**：`{code, msg, data}`  
**鉴权**：JWT，Header：`Authorization: Bearer <token>`

---

## 一、通用规范

### 响应码
| code | 说明 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录 |
| 403 | 无权限 |
| 404 | 不存在 |
| 500 | 服务器错误 |

### 统一响应
```json
{ "code": 200, "msg": "success", "data": {} }
```

---

## 二、用户模块

### 1. 注册
```
POST /api/user/register
Request: {
  username, password, height, weight, age, gender,
  goal,        // 减脂/增肌/控糖/维持
  avoid,       // 忌口
  allergy      // 过敏原
}
Response: { userId, token }
```

### 2. 登录
```
POST /api/user/login
Request: { username, password }
Response: { userId, token, profile }
```

### 3. 获取画像
```
GET /api/user/profile
Response: {
  userId, username, height, weight, age, gender,
  goal, avoid, allergy, bmr, targetCalories
}
```

### 4. 更新画像
```
PUT /api/user/profile
Request: { height, weight, age, gender, goal, avoid, allergy }
Response: { profile }
```

### 5. 个人主页
```
GET /api/user/{userId}/home
Response: {
  userId, username,
  publicRecords: [{ recordId, foodName, imageUrl, calories, likeCount, commentCount }],
  totalLikes, totalComments
}
```

---

## 三、记录模块

### 1. 拍照/文字录入
```
POST /api/record
Request: {
  foodName,      // 文字录入时传，拍照时可为空
  portion,
  mealType,      // 早/中/晚/加餐
  imageUrl,
  nutrition: { calories, protein, fat, carbs, fiber, sodium },
  visibility     // public/private，默认private
}
Response: { recordId }
```

### 2. 查询记录
```
GET /api/record?date=2025-01-01&mealType=午餐
Response: {
  records: [{ recordId, foodName, portion, mealType, imageUrl, nutrition, visibility, createdAt }],
  total: { calories, protein, fat, carbs, fiber, sodium }
}
```

### 3. 删除记录
```
DELETE /api/record/{recordId}
Response: {}
```

### 4. 修改可见性
```
PUT /api/record/{recordId}/visibility
Request: { visibility }   // public/private
Response: { recordId, visibility }
```

### 5. 手动修正
```
PUT /api/record/{recordId}
Request: { foodName, portion, nutrition }
Response: { record }
```

---

## 四、报告模块

### 1. 每日报告
```
GET /api/report/daily?date=2025-01-01
Response: {
  date,
  total: { calories, protein, fat, carbs, fiber, sodium },
  target: { calories, protein, fat, carbs },
  gap: { calories, protein, fat, carbs }
}
```

### 2. 一周报告
```
GET /api/report/weekly?start=2025-01-01
Response: {
  days: [{ date, calories, protein, fat, carbs }],
  trend: { calories: [], protein: [], fat: [], carbs: [] }
}
```

---

## 五、社交模块

### 1. 公开广场
```
GET /api/square?page=1&size=10&sort=time&mealType=午餐
Response: {
  total, page, size,
  records: [{
    recordId, userId, username, avatar,
    foodName, imageUrl, calories,
    likeCount, commentCount, liked,
    createdAt
  }]
}
```

### 2. 点赞/取消
```
POST /api/like/{recordId}
Response: { recordId, liked, likeCount }
```
> 已赞则取消，未赞则新增

### 3. 评论列表
```
GET /api/comment/{recordId}
Response: {
  comments: [{
    commentId, userId, username, avatar, content, createdAt,
    replies: [{
      commentId, userId, username, avatar,
      content, replyToUsername, createdAt
    }]
  }]
}
```

### 4. 发表评论
```
POST /api/comment
Request: {
  recordId,
  content,
  parentId    // 为空=一级评论；不为空=回复某条一级评论
}
Response: { commentId, content, createdAt }
```

### 5. 删除评论
```
DELETE /api/comment/{commentId}
Response: {}
```

---

## 六、AI微服务接口

### 1. 食物识别
```
POST /ai/recognize
Request: { imageBase64 } 或 { textDescription }
Response: {
  foods: [{
    name, portion,
    calories, protein, fat, carbs, fiber, sodium,
    confidence
  }]
}
```

### 2. RAG检索（内部）
```
POST /ai/rag
Request: { query }
Response: { chunks: [{ content, source }] }
```

### 3. 建议生成
```
POST /ai/advice
Request: {
  profile: { goal, bmr, targetCalories, avoid, allergy },
  todayIntake: { calories, protein, fat, carbs },
  gap: { calories, protein, fat, carbs }
}
Response: {
  advice,
  basedOn: [ "指南条目1", "指南条目2" ],
  safe: true
}
```

### 4. 菜谱生成
```
POST /ai/recipe
Request: {
  goal, budget, ingredients, avoid
}
Response: {
  breakfast: { name, ingredients, calories },
  lunch:     { name, ingredients, calories },
  dinner:    { name, ingredients, calories },
  shoppingList: []
}
```

### 5. 安全拦截
```
POST /ai/safety-check
Request: { advice }
Response: { safe, reason }
```

---

## 七、接口汇总

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户 | POST | /api/user/register | 注册 |
| 用户 | POST | /api/user/login | 登录 |
| 用户 | GET | /api/user/profile | 获取画像 |
| 用户 | PUT | /api/user/profile | 更新画像 |
| 用户 | GET | /api/user/{id}/home | 个人主页 |
| 记录 | POST | /api/record | 新增记录 |
| 记录 | GET | /api/record | 查询记录 |
| 记录 | DELETE | /api/record/{id} | 删除记录 |
| 记录 | PUT | /api/record/{id}/visibility | 修改可见性 |
| 记录 | PUT | /api/record/{id} | 手动修正 |
| 报告 | GET | /api/report/daily | 每日报告 |
| 报告 | GET | /api/report/weekly | 一周报告 |
| 社交 | GET | /api/square | 公开广场 |
| 社交 | POST | /api/like/{id} | 点赞/取消 |
| 社交 | GET | /api/comment/{id} | 评论列表 |
| 社交 | POST | /api/comment | 发表评论 |
| 社交 | DELETE | /api/comment/{id} | 删除评论 |
| AI | POST | /ai/recognize | 食物识别 |
| AI | POST | /ai/rag | RAG检索 |
| AI | POST | /ai/advice | 建议生成 |
| AI | POST | /ai/recipe | 菜谱生成 |
| AI | POST | /ai/safety-check | 安全拦截 |
