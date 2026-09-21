# 小组项目

如此强劲,震撼人心!
- 重要！！！ 开发前请确保掌握git语法和开源许可协议， 请查看<a href="gitcommit.md">git开发手册</a>和<a href="./LICENSE">许可协议</a>
项目名称： 
仓库地址：https://gitee.com/yanke_4_0/course_group_project
技术栈： Python Django（后端） + 微信小程序（前端）

小组成员：
| 姓名 | 联系方式 | 工作 |
| ---- | ------- | ---- |
|      |         |      | 

需求文档：（待定）

接口文档：<a href="api.md">api.md</a>

# 小程序前端

代码在 <a href="./miniprogram/">miniprogram/</a> 目录，三个页面覆盖社团的增删改查。

```
miniprogram/
├── app.js / app.json / app.wxss   # 全局配置和样式
├── utils/
│   ├── config.js                  # 后端地址、是否用假数据
│   ├── api.js                     # 请求封装 + 字段转换
│   └── mock.js                    # 后端没启动时的离线假数据
└── pages/
    ├── index/                     # 查：列表 + 搜索 + 下拉刷新，右下角「＋」新增
    ├── detail/                    # 查：详情，底部「编辑」「删除」
    └── edit/                      # 增 / 改：新增和编辑共用一套表单
```

| 功能 | 入口 | 接口 |
| --- | --- | --- |
| 查 | 列表页、详情页 | `GET /api/clubs/`、`GET /api/clubs/<id>/` |
| 增 | 列表页右下角 ＋ | `POST /api/clubs/` |
| 改 | 详情页「编辑」 | `PUT /api/clubs/<id>/` |
| 删 | 详情页「删除」（二次确认） | `DELETE /api/clubs/<id>/` |

**跑起来**

1. 先在仓库根目录启动后端：`python manage.py runserver`
2. 微信开发者工具 → 导入项目 → 选择**仓库根目录**（`miniprogramRoot` 已指向 `miniprogram/`）
3. 开发者工具右上角「详情 → 本地设置」勾选 **不校验合法域名**（因为请求的是 `http://127.0.0.1:8000`）
4. 后端没启动也能看界面：把 `miniprogram/utils/config.js` 里的 `useMock` 改成 `true`（这种模式下只有「查」能用，增删改会提示先关掉）

> 真机预览时 `127.0.0.1` 指向手机自己，需要把 `config.js` 里的 `baseUrl` 改成电脑的局域网 IP，例如 `http://192.168.1.10:8000`，并在微信后台配置或临时关闭域名校验。

# 许可协议： 
<a href="./LICENSE">MIT License</a>



Django 入门项目已经搭好，并写入了测试数据。接口 `GET /api/clubs/` 已验证能返回全部社团和管理员信息。

**查询接口**

- 方法：`GET`
- 地址：`http://127.0.0.1:8000/api/clubs/`
- 返回：全部社团名称、社团信息，以及对应管理员账号

**4 个后台用户（均可登录 Django Admin）**

| 用户名 | 所属社团 | 默认密码 |
| --- | --- | --- |
| 社团管理员1 | 篮球社 | `Admin123456` |
| 社团管理员2 | 摄影社 | `Admin123456` |
| 社团管理员3 | 音乐社 | `Admin123456` |
| 社团管理员4 | 志愿者社 | `Admin123456` |

后台地址：`http://127.0.0.1:8000/admin/`

**测试社团**：篮球社、摄影社、音乐社、志愿者社。

数据库使用根目录 `.sql` 中的配置：`test_914` / `root`。开发服务器目前在 **8000** 端口运行。若之后需要重新写入测试数据，可执行：

```powershell
python manage.py seed_data
```