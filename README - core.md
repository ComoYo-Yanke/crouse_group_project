# 贴身女仆 铃兰 · 本地 Agent

在原有 `my_first_agent.py` 基础上二次开发，**没有重写 Agent 内核**。
保留了原有的工作流程：同步工具循环 → 工具全部处理完 → 再流式生成最终回答。

---

## 一、项目结构

```
maid_agent/
├── my_first_agent.py    # Agent 内核（由原文件扩展而来）
│                        #   原有：client / MODEL / tools / tool_map / run_agent_stream / 命令行入口
│                        #   新增：web_search 工具、女仆 SYSTEM_PROMPT、事件流生成器
├── app.py               # FastAPI 后端：/api/chat(SSE) /api/reset /api/health
├── static/
│   └── index.html       # 女仆主题聊天页（单文件，无前端框架）
├── requirements.txt     # 依赖清单
└── README.md
```

## 二、安装依赖

```bash
# 1) 进入项目目录
cd f:\AIAgentPrograms\py_day_one\maid_agent

# 2) 激活你原来的虚拟环境（在上一级目录）
..\venv\Scripts\activate

# 3) 安装依赖
pip install -r requirements.txt
```

> ⚠️ **你的 Python 是 3.8.5**，所以这里用的是旧包名 `duckduckgo-search`。
> 新包名 `ddgs` 要求 Python 3.9+，在 3.8 上 pip 会直接报
> `No matching distribution found`。代码里两个包名都做了兼容，装哪个都能跑。

## 三、准备 Ollama

```bash
ollama serve            # 启动 Ollama（默认端口 11434）
ollama pull qwen3:8b    # 拉取模型（约 5GB，只需一次）
```

## 四、启动

```bash
python app.py
```

如果想跑原来的命令行版本（不带网页）：

```bash
python my_first_agent.py
```

## 五、访问地址

| 地址 | 说明 |
| --- | --- |
| http://127.0.0.1:8000 | 女仆聊天网页（根路径直接返回 HTML） |
| http://127.0.0.1:8000/docs | FastAPI 自动生成的接口文档 |
| http://127.0.0.1:8000/api/health | 自检：Ollama 是否可达、模型是否就绪 |

---

## 六、接口说明

### `POST /api/chat` — 聊天（SSE 流式）

请求体：

```json
{ "message": "今天北京天气怎么样？", "session_id": "abc-123" }
```

响应是 `text/event-stream`，逐帧推送：

```
data: {"type": "tool",  "name": "web_search"}
data: {"type": "delta", "text": "主人"}
data: {"type": "delta", "text": "，北京今天"}
data: {"type": "done",  "content": "主人，北京今天多云转晴，28 度呢。"}
```

| 事件类型 | 含义 |
| --- | --- |
| `tool` | 后台正在调用某个工具。**只给前端显示"在忙"，不含工具返回内容** |
| `delta` | 最终回答的增量 token，前端据此做打字机效果 |
| `done` | 本轮结束，`content` 是完整回答 |
| `error` | 出错，附带 `message` 和 `hint` |

### `POST /api/reset` — 清空会话记忆

```json
{ "session_id": "abc-123" }
```

### 命令行测试

```bash
curl -N -X POST http://127.0.0.1:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"你好\",\"session_id\":\"test\"}"
```

---

## 七、二次开发改动点（对照需求）

| 需求 | 落点 |
| --- | --- |
| 1. qwen3:8b + 11434 | `my_first_agent.py` 顶部 `MODEL` / `OLLAMA_BASE_URL` |
| 2. 联网搜索工具 | `my_first_agent.py` 的 `web_search()`，已注册进 `tools` 和 `tool_map` |
| 3. FastAPI 复用核心逻辑 | `app.py` 的 `/api/chat` 直接调用 `run_agent_events` |
| 4. 内置网页前端 | `static/index.html`，根路径 `/` 返回 |
| 5. 女仆人设 | `my_first_agent.py` 的 `SYSTEM_PROMPT` |
| 6. 工具强制规则 | 同上，`SYSTEM_PROMPT` 里的「工具使用规则」段 |
| 7. 不破坏原流程 | `run_agent_events()` 仍是：同步工具循环 → 流式生成 |
| 8. 内存记忆 | `app.py` 的 `SESSIONS` 字典（服务端内存，无数据库） |

### 关于原版的兼容

原版 `run_agent_stream(messages)` 是直接 `print` 的，浏览器拿不到 token。
现在它变成了**生成器**，同时保留了三个入口：

- `run_agent_events(messages)` —— 完整事件流（后端用）
- `run_agent_stream(messages)` —— 只吐文本增量（兼容原调用方式）
- `run_agent(messages)` —— 跑完返回完整字符串（兼容 `agent.py` 的写法）

三者的行为、参数、对 `messages` 的原地修改语义都和原版一致。

---

## 八、常见问题

**Q: 页面提示连不上铃兰 / 模型未就绪**
先跑 `ollama serve`，再 `ollama pull qwen3:8b`，然后访问 `/api/health` 看具体原因。

**Q: 搜索总是失败，铃兰说"查不到"** ⚠️ **这条一定要看**

实测你的网络环境**无法直连 DuckDuckGo**（`duckduckgo.com`、`html.duckduckgo.com`、
`lite.duckduckgo.com` 三个域名全部连接超时），而百度等国内站点是通的。
所以搜索工具本身没问题，是网络出不去。

**解决办法：给搜索工具单独挂代理。** 如果你本地有 Clash / V2Ray 之类的代理：

```bash
# Windows CMD（端口换成你自己的，Clash 常见是 7890）
set DDGS_PROXY=http://127.0.0.1:7890
python app.py
```

```bash
# PowerShell
$env:DDGS_PROXY="http://127.0.0.1:7890"
python app.py
```

不设 `DDGS_PROXY` 时，代码会自动沿用系统的 `HTTPS_PROXY` / `ALL_PROXY` 环境变量。
验证是否生效：

```bash
python -c "import my_first_agent as A; print(A.web_search('test', max_results=2))"
```

搜索失败时**不会**让 Agent 崩掉，也不会编造答案——铃兰会如实说"暂时查不到"，
这是符合需求6 的设计行为。但**搜索修好之前，实时信息类问题是查不到的**。

（实测记录：搜索失败时铃兰的回答是"暂时好像查不到最新的 AI 新闻呢…可能网络不太稳定"，
没有编造内容，行为符合预期。）

**Q: 搜索卡很久**
默认超时 8 秒，可用 `set SEARCH_TIMEOUT=15` 调整。
超时设小是为了搜索不通时快速失败，不至于让整轮对话卡住。

**Q: 女仆回答里带出 ` thinking...` 内容**
已内置 `_ThinkStripper` 过滤（qwen3 的思考块）。如果想更快，可以在
`SYSTEM_PROMPT` 末尾加一句 `/no_think`，让 qwen3 跳过思考、直接回答。

**Q: 记忆会存多久**
存在服务端内存 `SESSIONS` 里，重启进程就没了（符合"简易本地调试"的定位）。
每个会话最多保留 60 条历史消息，超出自动裁剪。

**Q: 想换模型**
改环境变量即可，不用动代码：

```bash
set AGENT_MODEL=qwen2.5:7b
python app.py
```

**Q: 想让手机也能访问**
把 `app.py` 末尾的 `host="127.0.0.1"` 改成 `host="0.0.0.0"`，
手机访问 `http://电脑局域网IP:8000`。
