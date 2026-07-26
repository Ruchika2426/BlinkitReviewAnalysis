import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv('../../.env')
import json

client = Groq()
try:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "test"}],
        model="gemma2-9b-it",
        max_tokens=7000,
    )
    print("Success Gemma2")
except Exception as e:
    print("Gemma Error:", e)

try:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "test"}],
        model="llama-3.1-8b-instant",
        max_tokens=7000,
    )
    print("Success Llama3.1")
except Exception as e:
    print("Llama Error:", e)
