from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

app = FastAPI(title="我的Vercel应用")

# 1. 一个简单的根路径端点
@app.get("/")
def read_root():
    return {"message": "🎉 你好！应用已在Vercel上成功运行！",
            "next_step": "尝试访问 /ask 端点向AI提问吧。"}

# 2. 定义接收提问的数据模型
class Question(BaseModel):
    question: str

# 3. 集成DeepSeek API的端点
@app.post("/ask")
def ask_ai(query: Question):
    """向DeepSeek AI提问"""
    api_key = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量读取密钥

    if not api_key:
        raise HTTPException(status_code=500, detail="未配置API密钥")

    # 调用DeepSeek API (假设使用Chat Completion接口)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # 请确认模型名称
        "messages": [{"role": "user", "content": query.question}],
        "stream": False
    }

    try:
        response = requests.post("https://api.deepseek.com/chat/completions",
                                 headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # 检查请求是否成功
        ai_response = response.json()
        return {
            "your_question": query.question,
            "ai_answer": ai_response["choices"][0]["message"]["content"]
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求AI服务时出错: {str(e)}")

# 4. 一个健康检查端点（Vercel等平台常用）
@app.get("/health")
def health_check():
    return {"status": "healthy"}