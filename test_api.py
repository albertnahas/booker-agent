#!/usr/bin/env python3
"""
Test script to verify the Booker Agent API functionality
"""

import requests
import json
import time
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Test the Booker Agent API")
    parser.add_argument("--api-url", default="http://localhost:8000", 
                        help="API URL (default: http://localhost:8000)")
    parser.add_argument("--city", default="Amsterdam", help="City to search")
    parser.add_argument("--test-mode", action="store_true", 
                        help="Run in test mode (information only, no booking)")
    parser.add_argument("--restaurant-name", help="Specific restaurant name to search for")
    
    # Contact information arguments
    parser.add_argument("--first-name", default="Test", help="First name for the reservation")
    parser.add_argument("--last-name", default="User", help="Last name for the reservation")
    parser.add_argument("--email", default="test@example.com", help="Email for the reservation")
    parser.add_argument("--phone-number", default="+31612345678", help="Phone number for the reservation")
    parser.add_argument("--booking-description", default="Test booking", 
                        help="Additional description or special requests")
    parser.add_argument("--latitude", type=float, help="Latitude coordinate for the search location")
    parser.add_argument("--longitude", type=float, help="Longitude coordinate for the search location")
                        
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Prepare booking request
    booking_request = {
        "city": args.city,
        "time": "18:30",
        "party_size": 2,
        "purpose": "dinner",
        "model": "gpt-4.1",
        "test_mode": args.test_mode,
        "first_name": args.first_name,
        "last_name": args.last_name,
        "email": args.email,
        "phone_number": args.phone_number,
        "booking_description": args.booking_description
    }
    
    # Add restaurant name if provided
    if args.restaurant_name:
        booking_request["restaurant_name"] = args.restaurant_name
        
    # Add coordinates if provided
    if args.latitude:
        booking_request["latitude"] = args.latitude
    if args.longitude:
        booking_request["longitude"] = args.longitude
    
    print(f"Testing API at {args.api_url}")
    print(f"Request payload: {json.dumps(booking_request, indent=2)}")
    
    try:
        # 1. Test API connectivity
        print("\nTesting API connectivity...")
        response = requests.get(f"{args.api_url}/")
        if response.status_code == 200:
            print("✅ API is accessible")
        else:
            print(f"❌ API returned status code {response.status_code}")
            return
        
        # 2. Start a booking
        print("\nStarting a booking request...")
        response = requests.post(f"{args.api_url}/book", json=booking_request)
        if response.status_code == 200:
            result = response.json()
            booking_id = result.get("booking_id")
            print(f"✅ Booking request accepted. Booking ID: {booking_id}")
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Booking request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # 3. Check status repeatedly
        print("\nChecking booking status (will check every 10 seconds)...")
        while True:
            response = requests.get(f"{args.api_url}/status/{booking_id}")
            if response.status_code == 200:
                status_result = response.json()
                status = status_result.get("status")
                message = status_result.get("message")
                print(f"Status: {status} - {message}")
                
                # If completed or failed, show details and break
                if status in ["completed", "failed"]:
                    print("\nFinal result:")
                    print(json.dumps(status_result, indent=2))
                    break
            else:
                print(f"❌ Status check failed with status code {response.status_code}")
                print(f"Response: {response.text}")
                break
            
            # Wait 10 seconds before next check
            time.sleep(10)
    
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API server is running.")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
