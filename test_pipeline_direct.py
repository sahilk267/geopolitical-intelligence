import httpx
import json
import os
import sys

def test_pipeline():
    base_url = os.getenv("TEST_PIPELINE_BASE_URL", "http://127.0.0.1:8000/api/v1")
    username = os.getenv("TEST_PIPELINE_USERNAME")
    password = os.getenv("TEST_PIPELINE_PASSWORD")

    if not username or not password:
        print("FAILED: TEST_PIPELINE_USERNAME and TEST_PIPELINE_PASSWORD must be set in the environment.")
        sys.exit(1)

    # 1. Login
    print("Logging in...")
    login_data = {
        "username": username,
        "password": password
    }
    response = httpx.post(f"{base_url}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Check categories
    print("Checking categories...")
    cat_response = httpx.get(f"{base_url}/reports/categories", headers=headers)
    print(f"Categories: {cat_response.text}")

    # 3. Run Pipeline
    print("Running pipeline for 'Regional News'...")
    pipeline_params = {
        "category": "Regional News",
        "region": "Global",
        "voice_id": "default",
        "generate_short": "true",
        "generate_presenter": "true"
    }
    
    # Using a long timeout because AI/Video takes time
    try:
        with httpx.Client(timeout=180.0) as client:
            run_response = client.post(
                f"{base_url}/pipeline/run-full", 
                params=pipeline_params,
                headers=headers
            )
            print(f"Pipeline Response Status: {run_response.status_code}")
            print(f"Pipeline Response Body: {json.dumps(run_response.json(), indent=2)}")
    except Exception as e:
        print(f"Pipeline call failed: {e}")

if __name__ == "__main__":
    test_pipeline()
