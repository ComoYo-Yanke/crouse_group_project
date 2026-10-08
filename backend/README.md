# 私人营养师系统 - SpringBoot 主后端

SpringBoot 2.7.18（兼容 JDK 8+），实现 api.md 中全部 `/api/*` 接口。

## 启动（推荐：IDEA）

1. 用 IDEA 打开 `backend` 目录（内置 Maven 自动导入依赖）
2. 运行 `NutritionistApplication`
3. 默认使用 **H2 内存数据库**，无需安装 MySQL，启动即跑
4. 演示账号自动初始化：`demo / 123456`、`xiaoming / 123456`

## 启动（命令行）

```bash
cd backend
mvn spring-boot:run
```

## 切换 MySQL

```bash
# 先创建数据库（或让连接参数 createDatabaseIfNotExist=true 自动建库）
mvn spring-boot:run -Dspring-boot.run.profiles=mysql
```

MySQL 连接配置见 `src/main/resources/application-mysql.yml`（默认 root/123456，按需修改）。

## 接口一览（api.md 二~五）

| 模块 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 用户 | POST | /api/user/register | 注册 |
| 用户 | POST | /api/user/login | 登录 |
| 用户 | GET | /api/user/profile | 获取画像（含 BMR/目标摄入） |
| 用户 | PUT | /api/user/profile | 更新画像 |
| 用户 | GET | /api/user/{id}/home | 个人主页 |
| 记录 | POST | /api/record | 新增记录 |
| 记录 | GET | /api/record?date=&mealType= | 查询记录+当日汇总 |
| 记录 | DELETE | /api/record/{id} | 删除记录 |
| 记录 | PUT | /api/record/{id}/visibility | 公开/私密 |
| 记录 | PUT | /api/record/{id} | 手动修正（标记 is_corrected） |
| 报告 | GET | /api/report/daily?date= | 每日报告（total/target/gap） |
| 报告 | GET | /api/report/weekly?start= | 一周报告 |
| 社交 | GET | /api/square?page=&size=&sort=&mealType= | 公开广场 |
| 社交 | POST | /api/like/{id} | 点赞/取消（toggle） |
| 社交 | GET | /api/comment/{id} | 评论列表（分楼） |
| 社交 | POST | /api/comment | 发表评论（最多两层） |
| 社交 | DELETE | /api/comment/{id} | 删除评论（级联删回复） |

## 关键实现

- **统一响应**：`{code, msg, data}`（`ApiResponse` + `GlobalExceptionHandler`）
- **JWT 鉴权**：`AuthInterceptor` 拦截 `/api/**`，白名单 `/api/user/register|login`
- **BMR 公式**（need.md 11.1）：男 `10W+6.25H-5A+5`，女 `10W+6.25H-5A-161`
- **目标摄入**（need.md 11.2）：减脂 `BMR×1.2-500`，增肌 `BMR×1.5+300`，维持/控糖 `BMR×1.3`
- **点赞防重**：`uk_user_record` 唯一索引 + toggle 语义
- **评论分楼**：parent_id 自关联，最多两层；删一级评论级联删回复
- **密码**：BCrypt 加密存储
- **表结构**：JPA 实体按 sql.md 建（user / food_record / like / comment）

## H2 控制台

启动后访问 http://localhost:8080/h2-console （JDBC URL: `jdbc:h2:mem:nutrition`，用户名 sa，密码空）
