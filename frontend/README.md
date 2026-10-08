# 私人营养师系统 - 前端

基于 **Vue 3 + Vite + Element Plus + Pinia + ECharts** 的前端项目。

## 启动

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## 代理配置

开发环境代理（见 `vite.config.js`）：
- `/api` → `http://localhost:8080`（SpringBoot 主后端）
- `/ai` → `http://localhost:8000`（Python FastAPI AI 微服务）

## 目录结构

```
frontend/
├── src/
│   ├── api/                # API 封装（对应 doc/api.md）
│   │   ├── request.js      # axios 实例：JWT 注入 + {code,msg,data} 统一处理
│   │   ├── user.js         # 用户模块
│   │   ├── record.js       # 记录模块
│   │   ├── report.js       # 报告模块
│   │   ├── square.js       # 社交模块（广场/点赞/评论）
│   │   └── ai.js           # AI 微服务（识别/建议/菜谱/安全）
│   ├── stores/
│   │   └── user.js         # Pinia 用户状态（token、画像）
│   ├── router/index.js     # 路由 + 登录守卫
│   ├── components/
│   │   └── layout/         # 整体布局（侧边栏+顶栏）
│   ├── views/
│   │   ├── auth/           # 登录/注册
│   │   ├── HomeView.vue    # 首页
│   │   ├── record/         # 记录录入（拍照/文字+AI识别）/记录管理
│   │   ├── report/         # 每日报告+一周趋势（ECharts）
│   │   ├── ai/             # AI 建议 / AI 菜谱
│   │   ├── square/         # 健康广场（点赞/评论分楼）
│   │   └── user/           # 个人画像 / 个人主页
│   └── assets/
└── vite.config.js
```

## 功能对应（doc/need.md）

| 模块 | 页面 | 状态 |
|------|------|------|
| 注册/登录 | `/login` `/register` | ✅ |
| 拍照/文字录入 + AI 识别 + 手动修正 | `/record/create` | ✅ |
| 记录管理 + 公开/私密设置 | `/record/list` | ✅ |
| 每日报告 + 一周趋势 | `/report` | ✅ |
| AI 建议（RAG）+ 安全拦截提示 | `/advice` | ✅ |
| AI 菜谱 + 购物清单 | `/recipe` | ✅ |
| 公开广场（排序/筛选/分页） | `/square` | ✅ |
| 点赞/取消 | 广场卡片 | ✅ |
| 评论分楼（一级+二级回复） | 广场评论抽屉 | ✅ |
| 个人画像（BMR/目标摄入展示） | `/profile` | ✅ |
| 个人主页（公开记录/统计） | `/user/:id` | ✅ |
