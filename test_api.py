from openai import OpenAI

# 连接本地 Ollama
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # 任意值即可，Ollama 不校验
)

# 先用 0.5b 测试（速度更快）
model = "qwen:0.5b"

print(f"🔌 正在测试模型: {model}")
print("-" * 40)

response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "你好，请用一句话介绍你自己"}
    ]
)

print("✅ API 调用成功！")
print(f"🤖 回复: {response.choices[0].message.content}")