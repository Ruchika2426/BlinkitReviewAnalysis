import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
client = Groq()

models = ["llama-3.1-8b-instant", "qwen/qwen3.6-27b", "openai/gpt-oss-20b", "openai/gpt-oss-120b", "llama-3.3-70b-versatile", "allam-2-7b"]

for m in models:
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=m,
            max_tokens=9000,
        )
        print(f"SUCCESS: {m} (supports 9000)")
    except Exception as e:
        print(f"FAIL {m}: {e}")
