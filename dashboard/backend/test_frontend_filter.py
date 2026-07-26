import requests
import json

url = "http://localhost:8000/api/ask-groq"
payload = {
    "prompt": "You are a Senior Product Researcher... Just output the JSON structure you would normally output."
}
# Actually I don't know the exact prompt the frontend uses.
