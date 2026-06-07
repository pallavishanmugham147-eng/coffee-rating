import urllib.request
import urllib.error
import json
import time
import sys

API_URL = "http://127.0.0.1:8000/api"

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        json_data = json.dumps(data).encode("utf-8")
    else:
        json_data = None
        
    try:
        with urllib.request.urlopen(req, data=json_data) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            err_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            err_body = e.reason
        return e.code, err_body
    except Exception as e:
        return 0, str(e)

def test_api():
    print("Waiting for API server to start...")
    # Try connecting to the server with retries
    retries = 10
    connected = False
    for i in range(retries):
        status, response = make_request(f"{API_URL}/coffees")
        if status == 200:
            connected = True
            break
        print(f"Server not ready yet (status={status}, error={response}), retrying in 1s...")
        time.sleep(1)
        
    if not connected:
        print("Error: Could not connect to the API server.")
        sys.exit(1)
        
    print("\n--- Test 1: Fetching all coffees ---")
    status, response = make_request(f"{API_URL}/coffees")
    assert status == 200, f"Expected 200, got {status}"
    assert len(response) == 4, f"Expected 4 initial coffees, got {len(response)}"
    print(f"Success! Found {len(response)} seeded coffees.")
    
    # Save the original votes count of coffee with ID 1
    original_votes = response[0]["votes"]
    coffee_id = response[0]["id"]
    coffee_name = response[0]["name"]
    print(f"Coffee ID {coffee_id} ({coffee_name}) has {original_votes} votes.")
    
    print("\n--- Test 2: Casting a vote ---")
    status, response = make_request(f"{API_URL}/coffees/{coffee_id}/vote", method="POST")
    assert status == 200, f"Expected 200, got {status}"
    assert response["votes"] == original_votes + 1, f"Expected {original_votes + 1} votes, got {response['votes']}"
    print(f"Success! Coffee ID {coffee_id} votes incremented to {response['votes']}.")
    
    print("\n--- Test 3: Adding a new coffee ---")
    new_coffee_data = {
        "name": "Cortado",
        "description": "Equal parts espresso and warm milk. Perfect microfoam.",
        "category": "Bold & Strong",
        "image_choice": "espresso"
    }
    status, response = make_request(f"{API_URL}/coffees", method="POST", data=new_coffee_data)
    assert status == 201, f"Expected 201, got {status}"
    assert response["name"] == "Cortado", f"Expected Cortado, got {response['name']}"
    assert response["image_path"] == "images/espresso.png", f"Expected images/espresso.png, got {response['image_path']}"
    print("Success! Created Cortado coffee successfully.")
    
    print("\n--- Test 4: Verify duplicate check ---")
    status, response = make_request(f"{API_URL}/coffees", method="POST", data=new_coffee_data)
    assert status == 400, f"Expected 400 duplicate error, got {status}"
    print(f"Success! Duplicate submission rejected with status 400 and detail: '{response.get('detail')}'")
    
    print("\n--- Test 5: Fetch list again to check size ---")
    status, response = make_request(f"{API_URL}/coffees")
    assert status == 200, f"Expected 200, got {status}"
    assert len(response) == 5, f"Expected 5 coffees now, got {len(response)}"
    print("Success! Coffee list contains 5 items.")
    
    print("\n--- Test 6: Database Reset ---")
    status, response = make_request(f"{API_URL}/coffees/reset", method="POST")
    assert status == 200, f"Expected 200, got {status}"
    print(f"Success! Reset returned: '{response.get('message')}'")
    
    # Confirm DB is reset (should be 4 items and votes back to original)
    status, response = make_request(f"{API_URL}/coffees")
    assert status == 200, f"Expected 200, got {status}"
    assert len(response) == 4, f"Expected 4 coffees after reset, got {len(response)}"
    assert response[0]["votes"] == original_votes, f"Expected votes to be reset to {original_votes}, got {response[0]['votes']}"
    print("Success! Verified coffee count and votes restored to initial defaults.")
    
    print("\nAll automated API tests passed successfully!")

if __name__ == "__main__":
    test_api()
