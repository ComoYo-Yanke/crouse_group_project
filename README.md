# 私人营养师系统

## 分支 feature/frontend-vue3

- **重要！！！** 开发前请确保掌握 git 语法和开源许可协议，请查看 <a href="./doc/gitcommit.md">git开发手册</a>、<a href="./doc/branchRule.md">分支规范</a> 和 <a href="./LICENSE">许可协议</a>

---

## 一、项目简介

一个 **AI 驱动、带社交互动的私人营养师系统**。解决「不知道自己吃了多少、缺什么、下一顿该吃什么」的问题，让普通人不用花钱预约营养师也能拿到可执行的饮食建议。

产品定位不是「卡路里记账 App」，而是有 AI 大脑、有社交互动的营养师社区：

| 能力 | 说明 |
| ---- | ---- |
| **会看** | 拍照或文字描述识别食物，自动估算营养 |
| **会算** | 每日营养摄入聚合，缺口可视化，一周趋势 |
| **会建议** | 基于《中国居民膳食指南(2022)》RAG 检索，给出个性化建议 |
| **会生成** | 按目标、预算、忌口生成一日三餐菜谱和购物清单 |
| **会互动** | 记录可设公开/私密，公开后进广场，支持点赞和分楼评论 |

**用户画像**：减脂、增肌、控糖/三高、普通白领、社交型用户。

**周期**：2 周 ｜ **小组**：4 人 ｜ **协作**：Gitee 分支管理

### 成员分工

| 成员 | 角色 | 核心职责 |
| ---- | ---- | -------- |
| CoMoYo | 项目经理 | comoyoyanke@outlook.com |
| 成员2 | 后端 A | SpringBoot 主：用户 + 记录 + 社交 |
| 成员3 | 后端 B | SpringBoot 辅：报告 + 聚合 + 联调 |
| 成员4 | AI + 测试 | FastAPI：识别 + RAG + 建议 + 菜谱 + 安全拦截 |

---

## 二、技术栈与架构

**Java SpringBoot + Python FastAPI + Vue3 + MySQL**

```
                    ┌─────────────────────────┐
                    │   浏览器 Vue3 + Element  │
                    │      localhost:5173      │
                    └────────┬───────┬────────┘
                     /api/*  │       │  /ai/*        ← Vite 开发代理
                             ▼       ▼
        ┌────────────────────────┐  ┌──────────────────────────┐
        │  SpringBoot 主服务      │  │  FastAPI AI 微服务        │
        │     localhost:8080     │  │      localhost:8000      │
        │  用户/记录/报告/社交     │  │  识别/建议/菜谱/安全       │
        └───────────┬────────────┘  └──────────┬───────────────┘
                    │                          │
                    ▼                          ▼
              ┌───────────┐            ┌──────────────┐
              │   MySQL   │            │  LLM API     │
              │  (可选)    │            │ (可不配置)     │
              └───────────┘            └──────────────┘
```

> AI 微服务被**前端直接调用**（走 Vite 代理），SpringBoot 目前不转发 AI 请求，两者是并列关系。

### 目录结构

```
course_group_project/
├── backend/      # SpringBoot 主服务（用户、记录、报告、社交）
├── ai-service/   # FastAPI AI 微服务（识别、建议、菜谱、安全拦截）
├── frontend/     # Vue3 + Element Plus + ECharts 前端
└── doc/          # 需求、接口、数据库、测试、分工等文档
```

---

## 三、快速开始

### 环境要求

| 依赖 | 版本 | 说明 |
| ---- | ---- | ---- |
| JDK | 8+ | 后端 pom 目标版本 1.8 |
| Maven | 3.6+ | 或用 IDEA 内置 Maven |
| Node.js | 18+ | Vite 6 要求 |
| Python | 3.8+ | AI 微服务 |
| MySQL | 8.0 | **可选**，默认走 H2 内存库 |

### 启动顺序

**① AI 微服务**（端口 8000）

```bash
cd ai-service
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

不配 key 也能启动，自动降级到本地规则/模板模式；接口文档见 http://localhost:8000/docs

若要接真实大模型，启动前设置环境变量（PowerShell 写法）：

```powershell
$env:OPENAI_API_KEY="你的key"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"   # 可换成智谱/DeepSeek/通义等兼容端点
$env:LLM_MODEL="gpt-4o-mini"                        # 需支持图片输入
```

**② SpringBoot 主服务**（端口 8080）

```bash
cd backend
mvn spring-boot:run
```

默认用 **H2 内存数据库**，无需装 MySQL，启动即跑。H2 控制台：http://localhost:8080/h2-console
（JDBC URL `jdbc:h2:mem:nutrition`，用户名 `sa`，密码空）

要换成 MySQL：

```bash
mvn spring-boot:run -Dspring-boot.run.profiles=mysql
```

连接配置在 `backend/src/main/resources/application-mysql.yml`，默认 `localhost:3306/nutritionist`、`root/123456`，按需修改。

**③ 前端**（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

> 三个服务要**同时运行**。前端所有请求走 Vite 代理：`/api/*` → 8080，`/ai/*` → 8000。

### 端口一览

| 服务 | 端口 | 地址 |
| ---- | ---- | ---- |
| 前端 Vue3 | 5173 | http://localhost:5173 |
| SpringBoot | 8080 | http://localhost:8080 |
| FastAPI AI | 8000 | http://localhost:8000/docs |
| MySQL | 3306 | 可选 |

---

## 四、功能模块

| 模块 | 主要功能 | 接口前缀 |
| ---- | -------- | -------- |
| 用户 | 注册、登录（JWT）、身体画像、个人主页 | `/api/user` |
| 记录 | 拍照/文字录入、手动修正、删除、公开/私密 | `/api/record` |
| 分析 | 每日聚合、缺口分析、一周趋势 | `/api/report` |
| 社交 | 公开广场、点赞（防重）、评论（分楼两层） | `/api/square` `/api/like` `/api/comment` |
| AI | 食物识别、RAG 建议、菜谱生成、安全拦截 | `/ai/*` |

**核心算法**（见 `doc/need.md` 附录）

- 基础代谢 BMR：男 `10W+6.25H-5A+5`，女 `10W+6.25H-5A-161`
- 目标摄入：减脂 `BMR×1.2-500`，增肌 `BMR×1.5+300`，维持/控糖 `BMR×1.3`
- 安全拦截规则：热量低于 BMR、极端节食（<800 kcal）、违禁药物、过敏原冲突

---

## 五、当前状态

项目骨架和全部页面/接口已写完，但**后端目前无法完整跑通**，已知阻塞：

1. **JWT 拦截器没有注册**。`AuthInterceptor` 写好了，但没有任何 `WebMvcConfigurer` 把它注册进去，导致拦截器从不执行、`UserContext` 永远为空。除注册/登录外，所有走 `UserContext.require()` 的接口都会返回 `401 未登录`。修复需要在 `com.nutritionist` 下补一个配置类调用 `addInterceptors`。
2. **演示账号没有初始化**。`backend/README.md` 写的 `demo / 123456`、`xiaoming / 123456` 实际不存在——代码里没有任何 `CommandLineRunner` 种子数据，H2 库每次启动都是空的，只能自己走注册流程。
3. **`/ai/rag` 不是真正的 RAG**。目前是 10 条硬编码膳食指南文本 + 关键词打分，没有向量化、没有向量库；图片识别在未配置 key 时返回占位结果。

> 这意味着「启动 → 登录 → 记一笔 → 看报告」这条主流程现在**走不通**，第 1 条修掉之后才能完整演示。

---

## 六、项目文档

| 文档 | 说明 |
| ---- | ---- |
| <a href="./doc/need.md">需求分析</a> | 功能需求、用例、验收标准 |
| <a href="./doc/api.md">接口文档</a> | SpringBoot + FastAPI 接口定义 |
| <a href="./doc/sql.md">数据库设计</a> | 表结构、ER关系、建表SQL |
| <a href="./doc/test.md">测试文档</a> | 测试用例、AI效果测试 |
| <a href="./doc/分工.md">分工文档</a> | 成员职责、周计划 |
| <a href="./doc/设想方向.md">设想方向</a> | 项目背景与目标 |
| <a href="./doc/答辩大纲.md">答辩大纲</a> | PPT结构与答辩要点 |
| <a href="./doc/演示脚本.md">演示脚本</a> | 现场演示流程 |

## 七、协作规范

- <a href="./doc/gitcommit.md">Git 开发手册</a>
- <a href="./doc/branchRule.md">分支规范</a>（`main` 禁止直接提交，一律走 PR）

## 许可协议

<a href="./LICENSE">MIT License</a>
