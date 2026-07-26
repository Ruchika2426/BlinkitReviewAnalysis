import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard', 'backend'))

from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

try:
    print("Testing /api/themes...")
    response = client.get("/api/themes")
    assert response.status_code == 200
    print(f"Success! Got {len(response.json())} themes.")

    print("\nTesting /api/reviews...")
    response = client.get("/api/reviews")
    assert response.status_code == 200
    print(f"Success! Got {len(response.json())} reviews.")

    print("\nTesting /api/reviews filter (theme=Delivery Cost Sensitivity)...")
    # Replace space with %20 for URL encoding manually if needed, but httpx (TestClient) handles dict params
    response = client.get("/api/reviews", params={"theme": "Delivery Cost Sensitivity"})
    assert response.status_code == 200
    print(f"Success! Filtered down to {len(response.json())} reviews.")

    print("\nTesting /api/insights...")
    response = client.get("/api/insights")
    assert response.status_code == 200
    print(f"Success! Content length: {len(response.json()['content'])} characters.")

    print("\nTesting /api/ask-groq...")
    response = client.post("/api/ask-groq", json={"prompt": "As a PM, what should I prioritize first?"})
    assert response.status_code == 200
    print(f"Success! Groq replied:\n{response.json()['response']}")

    print("\n✅ ALL TESTS PASSED!")
except Exception as e:
    print(f"❌ Test Failed: {e}")
