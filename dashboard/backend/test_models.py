import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
client = Groq()

models_to_test = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.6-27b"]

for m in models_to_test:
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": "test"}],
            model=m,
            max_tokens=8000,
        )
        print(f"Success {m}")
    except Exception as e:
        print(f"Error {m}: {e}")
