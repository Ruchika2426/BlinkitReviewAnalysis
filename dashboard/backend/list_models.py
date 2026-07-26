import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
client = Groq()
try:
    models = client.models.list()
    print("Available models:")
    for m in models.data:
        print(m.id)
except Exception as e:
    print(f"Error: {e}")
