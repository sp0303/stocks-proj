import requests
import json

base_url = "http://localhost:8000"
symbol = "RELIANCE.NS"

def test_endpoint(path):
    url = f"{base_url}{path}"
    print(f"Testing {url}...")
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("--- AI ENDPOINT TESTS ---")
    test_endpoint(f"/ai/lstm/{symbol}")
    test_endpoint(f"/ai/transformer/{symbol}")
    test_endpoint(f"/ai/consensus/{symbol}")
