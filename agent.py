import json
from openai import OpenAI
from datetime import datetime

# ========== 连接 Ollama ==========
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

# 用 0.5b 模型（速度快，适合学习）
# 如果你想换 1.8b，改成 "qwen:1.8b" 即可
MODEL = "qwen2.5:3b"

# ========== 定义工具函数 ==========
def get_current_time():
    """获取当前日期和时间"""
    return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")

def calculate(expression: str):
    """执行数学计算"""
    try:
        # 注意：eval 有安全风险，这里仅用于学习演示
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

# ========== 工具注册表 ==========
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
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
            "name": "calculate",
            "description": "执行数学计算，支持加减乘除等运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，例如 '3 + 5 * 2' 或 '100 / 4'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]

# 工具名称 → 实际函数的映射
tool_map = {
    "get_current_time": get_current_time,
    "calculate": calculate
}

# ========== Agent 主循环 ==========
def run_agent(user_input):
    """运行 Agent，处理用户输入"""
    
    # 初始化消息
    messages = [
        {"role": "system", "content": "你是一个智能助手，可以使用工具帮助用户。"},
        {"role": "user", "content": user_input}
    ]
    
    # Agent Loop
    while True:
        # 调用 LLM
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # 如果没有工具调用，直接返回最终回答
        # tool_calls是调用工具请求
        if not message.tool_calls:
            return message.content
        
        # 有工具调用：把 LLM 的响应加入消息历史
        messages.append(message)
        
        # 执行每个工具调用
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            
            print(f"🔧 调用工具: {func_name}({func_args})")
            
            # 执行工具函数
            result = tool_map[func_name](**func_args)
            
            # 把工具执行结果加入消息历史
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # 继续循环，LLM 会根据工具结果生成最终回答

# ========== 交互式运行 ==========
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 你的第一个 AI Agent 已启动")
    print(f"📦 当前模型: {MODEL}")
    print("📌 输入 'quit' 或 'exit' 退出")
    print("=" * 50)
    
    while True:
        user_input = input("\n👤 你: ").strip()
        
        if user_input.lower() in ["quit", "exit", "q"]:
            print("👋 再见！")
            break
        
        if not user_input:
            continue
        
        print("🤔 Agent 思考中...")
        result = run_agent(user_input)
        print(f"🤖 Agent: {result}")