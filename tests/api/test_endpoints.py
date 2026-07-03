from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_endpoints():
    # 1. Config
    resp = client.get("/semantic-config")
    print("Config GET:", resp.json())

    # 2. Index
    payload = {
        "items": [
            {
                "id": "doc1",
                "text": "Biology is the study of life",
                "descriptor": {"domain": "Science -> Biology", "intent": "Education"}
            },
            {
                "id": "doc2",
                "text": "Finance deals with money and investments",
                "descriptor": {"domain": "Finance", "intent": "Informational"}
            }
        ]
    }
    resp = client.post("/semantic-index", json=payload)
    print("Index POST:", resp.json())

    # 3. Search (deterministic)
    resp = client.get("/semantic-search?q=Biology")
    print("Search GET:", resp.json())

if __name__ == "__main__":
    test_endpoints()
