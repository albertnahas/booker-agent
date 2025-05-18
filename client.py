#!/usr/bin/env python3
"""
Example client script for interacting with the Booker Agent API.
This can be run from any machine with Python and requests installed.
"""

import requests
import time
import sys
import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Restaurant Booking API Client")
    parser.add_argument("--api-url", required=True, help="Base URL of the API (e.g., http://localhost:8000)")
    parser.add_argument("--city", default="Amsterdam", help="City for restaurant search")
    parser.add_argument("--date", help="Booking date (YYYY-MM-DD)")
    parser.add_argument("--time", default="18:00", help="Booking time (HH:MM)")
    parser.add_argument("--party-size", type=int, default=2, help="Number of people")
    parser.add_argument("--purpose", default="dinner", help="Purpose of reservation")
    parser.add_argument("--model", default="gpt-4o", help="LLM model to use")
    parser.add_argument("--test", action="store_true", help="Run in test mode")
    parser.add_argument("--check-only", help="Only check status of existing booking ID")
    return parser.parse_args()

def start_booking(api_url, params):
    """Start a new booking using the API."""
    try:
        response = requests.post(f"{api_url}/book", json=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error starting booking: {e}")
        sys.exit(1)

def check_status(api_url, booking_id):
    """Check the status of an existing booking."""
    try:
        response = requests.get(f"{api_url}/status/{booking_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error checking status: {e}")
        return None

def main():
    args = parse_args()
    
    # Check if we're only checking an existing booking
    if args.check_only:
        print(f"Checking status of booking {args.check_only}...")
        status = check_status(args.api_url, args.check_only)
        if status:
            print(json.dumps(status, indent=2))
        return
    
    # Prepare the booking request
    booking_request = {
        "city": args.city,
        "time": args.time,
        "party_size": args.party_size,
        "purpose": args.purpose,
        "model": args.model,
        "test_mode": args.test
    }
    
    # Add date if provided
    if args.date:
        booking_request["date"] = args.date
    
    # Start the booking
    print("Starting booking...")
    booking_response = start_booking(args.api_url, booking_request)
    booking_id = booking_response["booking_id"]
    print(f"Booking started with ID: {booking_id}")
    
    # Poll for status updates
    print("Polling for status updates (press Ctrl+C to stop)...")
    try:
        while True:
            status = check_status(args.api_url, booking_id)
            if status:
                current_status = status["status"]
                message = status["message"]
                print(f"Status: {current_status} - {message}")
                
                # If booking is completed or failed, break the loop
                if current_status in ["completed", "failed"]:
                    print("\nFinal result:")
                    print(json.dumps(status, indent=2))
                    break
            
            # Wait before polling again
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nStopped polling. You can check the status later with:")
        print(f"  {sys.argv[0]} --api-url {args.api_url} --check-only {booking_id}")

if __name__ == "__main__":
    main()
