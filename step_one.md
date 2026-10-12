# Python Agent 快速入门

> 本文档记录了一个基于本地 Ollama 模型的 Tool Calling Agent 从零到一的完整实现过程。  
> 适用读者：已了解 Python 基础，想理解 Agent 核心运行机制而非依赖框架的开发者。

---

## 背景与目标

实现一个极简的 Tool Calling Agent，目标是：

- 理解 Agent 的核心运行机制（Agent Loop）
- 不依赖任何高级框架（如 LangGraph）
- 支持自定义工具（时间查询、天气查询）
- 通过 LLM 自主判断是否调用工具以及如何整合结果

---

## 整体架构设计

一个最简单的 Agent 至少包含四个部分：
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ 用户输入 │ ──→ │ LLM │ ──→ │ 工具执行 │ ──→ │ 输出结果 │
└─────────┘ └─────────┘ └─────────┘ └─────────┘
│ ↑
│ ┌────────────┘
└─────│ 工具说明书（tools）
└─────────────────────────────┘

**核心交互流程：**
用户输入
↓

思考和分析需求（LLM 判断是否需要工具）
↓

查询工具集 → 匹配可用工具
↓

调用工具 → 获取结果（2~4 可能反复执行）
↓

整合所有工具结果
↓

包装并输出最终回答

text

---

## 核心流程（Agent Loop）
第 1 步：初始化 messages，包含 system 和 user 消息
第 2 步：调用 LLM，传入 messages 和 tools
第 3 步：检查返回的 message 中是否包含 tool_calls
第 4 步：如果有 tool_calls：
4a. 将 LLM 的响应追加到 messages
4b. 遍历每个 tool_call，执行对应的 Python 函数
4c. 将工具执行结果追加到 messages
4d. 回到第 2 步
第 5 步：如果没有 tool_calls：
5a. 将 LLM 的最终回答作为结果
5b. 跳出循环

text

---

## 关键实现与代码片段

### 1. 初始化与连接

```python
import json
from openai import OpenAI
from datetime import datetime

# 连接本地 Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",  # 本地 Ollama
    api_key="ollama"                       # 任意值即可
)

# 如果用云服务，替换为：
# client = OpenAI(
#     base_url="https://api.deepseek.com/v1",
#     api_key="sk-你的密钥"
# )
# MODEL = "deepseek-chat"

MODEL = "qwen2.5:3b"
2. 工具函数与工具集
python
def get_current_time():
    """获取当前日期和时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_weather_for_city(city):
    """查询城市天气（模拟数据）"""
    if city == "北京":
        return "多云转晴 20摄氏度"
    else:
        return "阴转多云 19摄氏度"


# 工具说明书（告诉 LLM 有哪些工具可用）
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间，精确到秒",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_for_city",
            "description": "通过用户输入的城市查询天气信息，包含天气描述和温度",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名"
                    }
                }
            },
            "required": ["city"]
        }
    }
]

# 工具名称 → 实际函数的映射
tool_map = {
    "get_current_time": get_current_time,
    "get_weather_for_city": get_weather_for_city
}
3. 主循环与 Agent 调用
python
if __name__ == "__main__":
    print("=" * 50)
    print(f"模型启动成功: {MODEL}")
    print("开始对话（输入 'quit' 退出）")
    print("=" * 50)

    while True:
        user_input = input("\n> 我: ")
        if user_input.lower() == "quit":
            print("bye")
            break

        print("thinking...")

        # 初始化消息
        messages = [
            {"role": "system", "content": "你是一个智能助手，可以使用工具帮助用户。"},
            {"role": "user", "content": user_input}
        ]

        result = None

        # Agent 内循环
        while True:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message

            # 没有工具调用 → 得到最终答案
            if not message.tool_calls:
                result = message.content
                break

            # 有工具调用 → 将 LLM 响应加入消息历史
            messages.append(message)

            # 执行所有工具调用
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name        # 获取函数名
                func_args = json.loads(tool_call.function.arguments)  # 解析参数
                func = tool_map[func_name]                 # 通过名称找到函数
                result_data = func(**func_args)            # 调用函数

                # 将工具执行结果加入消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_data
                })

            # 循环继续，LLM 根据工具结果生成最终回答

        print(f"AI: {result}")
踩坑记录与解决方法
问题	原因	解决方法
qwen:0.5b 不支持工具调用	小模型不具备 Function Calling 能力	换用 qwen2.5:3b 或 qwen2.5:7b
pip install openai 报错 jiter 版本找不到	pip 版本过旧（20.1.1）	升级 pip：python -m pip install --upgrade pip
if not messages.tool_calls: 报错	messages 是列表，没有 tool_calls 属性	改为 if not message.tool_calls:
Agent 内循环无法退出	没有在“无工具调用”时跳出循环	在 result = message.content 后加 break
模型不支持中文	使用英文模型（如 Llama）	换用 Qwen 系列模型
下一步改进方向
1. 增加多轮对话记忆
当前每次提问都是独立会话，Agent 不记得上一轮的内容。
改进方式：将 messages 从内循环提升到外循环，实现上下文记忆。

2. 增加更多工具
文件读写

网页搜索

数据库查询

真实天气 API（如和风天气、OpenWeatherMap）

3. 引入 LangGraph
手写 Agent Loop 已经跑通后，可以学习 LangGraph 如何解决更复杂的问题：

条件分支

并行执行

人机交互（Human-in-the-loop）

状态持久化

总结
通过这个极简实现，你已经掌握了 Agent 最核心的本质：

Agent = LLM + State（messages）+ Tools + Control Loop

这四者的组合，构成了所有 Agent 系统的基础。无论未来框架如何变化，这个核心认知都不会过时。

text

---

