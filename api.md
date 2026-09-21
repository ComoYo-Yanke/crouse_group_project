# 接口文档

开发服务器：`http://127.0.0.1:8000`

## 1. 获取社团列表

小程序列表页 / 详情页都走这个接口。

- **方法**：`GET`
- **地址**：`/api/clubs/`
- **请求参数**：无

**返回示例**

```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "name": "篮球社",
      "description": "每周三、周六下午在体育馆训练。",
      "category": "体育",
      "founded_date": "2019-09-01",
      "location": "体育馆 3 号场",
      "administrators": [
        {
          "id": 1,
          "real_name": "张伟",
          "username": "社团管理员1",
          "is_staff": true,
          "phone": "13800000001",
          "email": "zhangwei@example.com"
        }
      ]
    }
  ]
}
```

**字段说明**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `count` | int | 社团总数 |
| `results[].id` | int | 社团 ID，详情页靠它定位 |
| `results[].name` | string | 社团名称 |
| `results[].description` | string | 社团简介 |
| `results[].category` | string | 社团类型 |
| `results[].founded_date` | string | 成立日期 `YYYY-MM-DD` |
| `results[].location` | string | 活动地点，可能为空字符串 |
| `results[].administrators` | array | 该社团的管理员列表，可能为空数组 |
| `administrators[].real_name` | string | 管理员姓名 |
| `administrators[].username` | string | 后台登录账号 |
| `administrators[].is_staff` | bool | 是否能登录 Django Admin |
| `administrators[].phone` | string | 联系电话 |
| `administrators[].email` | string | 邮箱 |

## 2. 获取单个社团

- **方法**：`GET`
- **地址**：`/api/clubs/<id>/`
- **返回**：单个社团对象，结构同 `results[]` 中的一项
- **错误**：`404` → `{ "detail": "社团不存在" }`

## 3. 新增社团

- **方法**：`POST`
- **地址**：`/api/clubs/`
- **请求体**（`Content-Type: application/json`）：

```json
{
  "name": "篮球社",
  "category": "体育",
  "founded_date": "2019-09-01",
  "location": "体育馆 3 号场",
  "description": "每周三、周六下午训练。"
}
```

- **成功**：`201`，返回新建的社团对象（含 `id`）
- **失败**：`400`

```json
{
  "detail": "表单校验失败",
  "errors": { "name": ["这个字段是必填项。"] }
}
```

## 4. 修改社团

- **方法**：`PUT`（或 `PATCH`，处理方式相同）
- **地址**：`/api/clubs/<id>/`
- **请求体**：同新增，需要提交完整字段
- **成功**：`200`，返回更新后的社团对象
- **失败**：`400` 校验失败（同上）、`404` 社团不存在

## 5. 删除社团

- **方法**：`DELETE`
- **地址**：`/api/clubs/<id>/`
- **成功**：`200` → `{ "detail": "已删除社团「篮球社」" }`
- **失败**：`404` 社团不存在

> 关联的 `ClubAdministrator` 是 `on_delete=CASCADE`，删除社团会连带删除它的管理员记录。

## 其他说明

- **鉴权**：写接口目前没有登录校验，任何能访问到服务的人都能增删改。课程演示够用，上线前必须补权限。
- **CSRF**：写接口用了 `@csrf_exempt`，因为小程序不走 Django 的 CSRF token 流程。
- 字段校验直接复用后台表单 `clubs/forms.py` 的 `ClubForm`，所以网页端和小程序的校验规则一致。
- 字段要求：`name` / `category` / `founded_date` / `description` 必填，`location` 可空。
- 待补充：管理员（`administrators`）目前只能通过 Django Admin 维护，接口不支持增删改；也没有分页和按类型筛选。
