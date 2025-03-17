"""
Simple test script for EEG Task Data Server API.

This script sends a test request to the server and verifies the response.
"""

import requests
import json
import argparse
import sys
import os
from datetime import datetime

def test_api(url, participant_id="test", session_id="001"):
    """Test the API by sending a sample request and printing the response."""
    
    # Create sample data with current timestamp
    current_time = datetime.now().timestamp() * 1000  # Convert to milliseconds
    test_data = {
        "id": participant_id,
        "session": session_id,
        "data": [
            {"time": current_time, "value": 0.5, "marker": "test_stimulus_1"},
            {"time": current_time + 100, "value": 0.7, "marker": "test_response_1"},
            {"time": current_time + 200, "value": 0.3, "marker": "test_stimulus_2"},
            {"time": current_time + 300, "value": 0.9, "marker": "test_response_2"}
        ]
    }
    
    print(f"Sending test data to {url}...")
    print(f"Participant ID: {participant_id}, Session ID: {session_id}")
    print(f"Number of data points: {len(test_data['data'])}")
    
    try:
        # Send POST request to the API
        response = requests.post(
            url + "/submit_data", 
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response status code
        if response.status_code == 200:
            print("\n✅ SUCCESS: Server responded with status code 200")
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2))
            
            # Verify if the file was created/updated
            result = response.json()
            if os.path.exists(result.get('filename', '')):
                print(f"\nFile created/updated: {result.get('filename')}")
                print(f"Total records in file: {result.get('total_records')}")
            else:
                print(f"\n⚠️ Warning: File not found at {result.get('filename')}")
                
        else:
            print(f"\n❌ ERROR: Server responded with status code {response.status_code}")
            print("\nResponse JSON:")
            print(json.dumps(response.json(), indent=2))
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to server at {url}")
        print("Make sure the server is running and the URL is correct.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False
        
    return response.status_code == 200

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the EEG Task Data Server API")
    parser.add_argument("--url", default="http://localhost:5000", help="Server URL (default: http://localhost:5000)")
    parser.add_argument("--id", default="test", help="Participant ID (default: test)")
    parser.add_argument("--session", default="001", help="Session ID (default: 001)")
    
    args = parser.parse_args()
    
    # Run the test
    success = test_api(args.url, args.id, args.session)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
