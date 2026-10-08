# AI 微服务（Python FastAPI）

## 启动

```bash
cd ai-service
pip install -r requirements.txt
uvicorn main:app --port 8000 --reload
```

接口文档（自动生成）：http://localhost:8000/docs

## LLM 配置（可选）

默认使用**本地模式**（内置食物营养表 + 膳养指南知识库 + 模板建议），无需任何 Key 即可演示完整流程。

配置真实 LLM 后自动升级：

```powershell
# OpenAI 兼容接口均可（OpenAI / 智谱 / DeepSeek / 通义千问等）
$env:OPENAI_API_KEY="sk-xxx"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"   # 或其他兼容服务
$env:LLM_MODEL="gpt-4o-mini"                        # 需支持视觉才能拍照识别
uvicorn main:app --port 8000 --reload
```

## 接口（doc/api.md 六）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /ai/recognize | 食物识别（imageBase64 / textDescription） |
| POST | /ai/rag | RAG 检索膳食指南 |
| POST | /ai/advice | 建议生成（含安全拦截） |
| POST | /ai/recipe | 菜谱生成 |
| POST | /ai/safety-check | 安全拦截检查 |
