import requests
import json
import sys

def test_api():
    url = "http://localhost:8000/api/lbw-decision"
    
    try:
        with open("data/sample_input_lbw.json", "r") as f:
            input_data = json.load(f)
    except Exception as e:
        print(f"Error loading sample data: {e}")
        sys.exit(1)
    
    try:
        response = requests.post(url, json=input_data)

        if response.status_code == 200:
            print("API test successful!")
            print("\nResponse:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"API test failed with status code: {response.status_code}")
            print("\nError:")
            print(response.text)
    except Exception as e:
        print(f"Error making API request: {e}")
        print("\nMake sure the API server is running with 'python dev_server.py'")

if __name__ == "__main__":
    test_api()