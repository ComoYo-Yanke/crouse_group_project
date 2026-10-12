import json
import time
from openai import OpenAI
from datetime import datetime

# ========== 连接 Ollama ==========
# 创建OpenAI客户端，连接到本地运行的Ollama服务
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama的API地址
    api_key="ollama"  # Ollama不需要真实的API key，填什么都行
)
MODEL = "qwen2.5:3b"  # 使用的模型名称

# ========== 工具函数 ==========
def get_current_time():
    """获取当前时间，返回格式化的日期时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_weather_for_city(city):
    """根据城市名返回天气信息（模拟数据）"""
    if city == "北京":
        return "多云转晴 28摄氏度"
    else:
        return "阴转多云 21摄氏度"



# ========== 工具定义（说明书） ==========
# tools 是一个"说明书"，告诉AI有哪些工具可以用
# AI看到这个说明书后，如果需要用到工具，就会说"我要调用XXX工具"
tools = [
    {
        "type": "function",  # 固定写法，表示这是一个函数工具
        "function": {
            "name": "get_current_time",  # 工具名称
            "description": "获取当前的日期和时间，精确到秒",  # 工具描述
            "parameters": {  # 参数说明（JSON Schema格式）
                "type": "object",  # 参数是一个对象
                "properties": {},  # 这个工具没有参数，所以是空对象
                "required": []  # 没有必填参数
            }
        }
    },
    {
        "type": "function",
        "function":{
            "name": "get_weather_for_city",
            "description": "通过用户输入的城市查询天气信息,包含天气描述和温度",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {  # 定义city参数
                        "type": "string",
                        "description": "城市名"
                    }
                }
            },
            "required": ["city"]  # city是必填参数
        }
    }
]

# ========== 工具映射表 ==========
# 把工具名称和实际的函数对应起来
# 就像电话号码本：通过名字找到对应的函数
tool_map = {
    "get_current_time": get_current_time,
    "get_weather_for_city": get_weather_for_city,
}

# ========== 核心：运行Agent（支持流式输出） ==========
def run_agent_stream(messages):
    """
    运行Agent，支持流式输出
    返回：AI的完整回答
    """
    
    # ===== 第1步：判断是否需要工具 =====
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto" # 自动判断
    )
    
    message = response.choices[0].message
    
    # ===== 第2步：没有工具调用 =====
    if not message.tool_calls:
        # 流式输出
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=True
        )
        
        full_response = ""
        print("ai: ", end="", flush=True)
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
                full_response += delta.content
        print()
        return full_response
    
    # ===== 第3步：有工具调用，处理工具 =====
    # 把message转换成字典格式，添加到消息列表
    messages.append({
        "role": "assistant",
        "content": message.content,  # 可能为None
        "tool_calls": [
            {
                "id": t.id,
                "function": {
                    "name": t.function.name,
                    "arguments": t.function.arguments
                },
                "type": t.type
            }
            for t in message.tool_calls
        ]
    })
    
    # 执行工具调用
    for t in message.tool_calls:
        
        func_name = t.function.name
        func_args = json.loads(t.function.arguments)
        func = tool_map[func_name]
        result_data = func(**func_args)
        print(f"调用工具:{func_name}\n")
        # 添加工具结果到消息列表
        messages.append({
            "role": "tool",
            "tool_call_id": t.id,
            "content": result_data
        })
    
    # ===== 第4步：生成最终回答（流式） =====
    stream = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True
    )
    
    full_response = ""
    print("ai: ", end="", flush=True)
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            full_response += delta.content
    print()
    
    return full_response


# ========== 主程序入口 ==========
if __name__ == "__main__":
    print("="*50)
    print(f"模型启动成功:{MODEL}")
    print("开始对话")
    print("="*50)
    
    # 初始化消息列表
    # system消息：设定AI的角色和任务
    messages = [
        {"role": "system", "content": "你是一个ai智能体,可以使用工具回答用户。用户告诉你任何关于你是谁的信息或名字相关或模型时,都要回答我是智能体助手,不能暴露你是Qwen或者其他模型"},
    ]
    
    # 主对话循环
    while True:
        # 获取用户输入
        user_input = input("\n>")
        
        # 退出命令
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nbye\n")
            break
        
        print("< thinking...")  # 提示用户AI正在思考
        
        # 把用户输入添加到消息列表
        messages.append({"role": "user", "content": user_input})
        
        # 调用流式Agent，获取完整回答
        # 这个函数会：
        # 1. 判断是否需要工具
        # 2. 如果需要，调用工具
        # 3. 流式输出最终回答
        # 4. 返回完整回答
        
        ai_response = run_agent_stream(messages)
        
        # 把AI的完整回答添加到消息列表
        # 这样下一轮对话AI就能记住之前说过什么
        messages.append({"role": "assistant", "content": ai_response})
        # 可选：显示当前对话轮次，方便调试
        user_count = len([m for m in messages if m['role'] == 'user'])
        # print(f"[第{user_count}轮对话]")