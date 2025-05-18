import os
import argparse
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from browser_use import Agent, Browser, BrowserConfig, Controller
import asyncio
from dotenv import load_dotenv
import warnings
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")

# Define the output format as Pydantic models
class RestaurantDetails(BaseModel):
    name: str
    address: str
    phone_number: Optional[str] = None
    rating: Optional[float] = None
    price_range: Optional[str] = None
    cuisine_type: Optional[str] = None
    popular_dishes: Optional[List[str]] = None
    opening_hours: Optional[str] = None

class BookingDetails(BaseModel):
    confirmation_number: Optional[str] = None
    date: str
    time: str
    party_size: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    special_requests: Optional[str] = None
    status: str = "confirmed"

class BookingResult(BaseModel):
    restaurant: RestaurantDetails
    booking: Optional[BookingDetails] = None
    additional_notes: Optional[str] = None

def parse_arguments():
    """Parse command line arguments for the restaurant booking."""
    parser = argparse.ArgumentParser(description="Automated restaurant booking")
    
    parser.add_argument("--city", default="Amsterdam", help="City for restaurant search (default: Amsterdam)")
    parser.add_argument("--date", help="Booking date (format: YYYY-MM-DD, defaults to tomorrow)")
    parser.add_argument("--time", help="Booking time (format: HH:MM, defaults to 18:00)")
    parser.add_argument("--party_size", type=int, help="Number of people in the party (defaults to 2)")
    parser.add_argument("--purpose", default="dinner", help="Purpose of the reservation (default: dinner)")
    parser.add_argument("--model", default="gpt-4.1", choices=["claude-3-5-sonnet-latest", "gpt-4.1"],
                       help="LLM model to use: 'claude-3-5-sonnet-latest' or 'gpt-4.1'")
    parser.add_argument("--test", action="store_true", help="Run in test mode without confirming booking")
    parser.add_argument("--restaurant-name", help="Specific restaurant name to search for")
    
    # Contact information arguments
    parser.add_argument("--first-name", help="First name for the reservation")
    parser.add_argument("--last-name", help="Last name for the reservation")
    parser.add_argument("--email", help="Email for the reservation")
    parser.add_argument("--phone-number", help="Phone number for the reservation")
    parser.add_argument("--booking-description", help="Additional description or special requests for the booking")
    parser.add_argument("--latitude", type=float, help="Latitude coordinate for the search location")
    parser.add_argument("--longitude", type=float, help="Longitude coordinate for the search location")
    
    return parser.parse_args()

async def book_restaurant(*, city="Amsterdam", date=None, time="18:00",
                    party_size=2, purpose="dinner", model="gpt-4.1", test_mode=False,
                    first_name=None, last_name=None, email=None, phone_number=None,
                    booking_description=None, restaurant_name=None, latitude=None, longitude=None):
    """Book a restaurant.
    
    Args:
        city (str): City to search for restaurants (default: Amsterdam)
        date (str): Booking date in YYYY-MM-DD format (default: tomorrow)
        time (str): Booking time in HH:MM format (default: 18:00)
        party_size (int): Number of people in the party (default: 2)
        purpose (str): Purpose of the reservation (default: dinner)
        model (str): LLM model to use (default: claude-3-5-sonnet-latest)
        test_mode (bool): Whether to run in test mode without confirming booking
        first_name (str, optional): First name for the reservation
        last_name (str, optional): Last name for the reservation
        email (str, optional): Email for the reservation
        phone_number (str, optional): Phone number for the reservation
        booking_description (str, optional): Additional description or special requests for the booking
        restaurant_name (str, optional): Specific restaurant name to search for
        latitude (float, optional): Latitude coordinate for the search location
        longitude (float, optional): Longitude coordinate for the search location
    
    Returns:
        str: JSON-formatted BookingResult containing restaurant details and booking information (if not in test mode)
    """
    
    # Initialize browser - use environment variable for headless mode if available
    headless = os.environ.get('BROWSER_HEADLESS', 'false').lower() == 'true'
    browser_config = BrowserConfig(headless=headless)
    browser = Browser(config=browser_config)
    
    # Select LLM based on provided model parameter
    if model.startswith("gpt"):
        llm = ChatOpenAI(model=model)
    else:
        llm = ChatAnthropic(model_name=model)
    
    # Add geocoding functionality to convert city name to coordinates

    def get_coordinates(city_name):
        """
        Get latitude and longitude coordinates for a given city name.
        
        Args:
            city_name (str): Name of the city
            
        Returns:
            tuple: (latitude, longitude) or (None, None) if not found
        """
        try:
            # Initialize Nominatim geocoder with a user agent
            geolocator = Nominatim(user_agent="restaurant-booking-app")
            
            # Get location information
            location = geolocator.geocode(city_name)
            
            if location:
                return (location.latitude, location.longitude)
            else:
                print(f"Could not find coordinates for {city_name}")
                return (None, None)
        except (GeocoderTimedOut, GeocoderUnavailable) as e:
            print(f"Geocoding error: {e}")
            return (None, None)

    # Use provided coordinates if available, otherwise geocode the city
    if latitude is not None and longitude is not None:
        print(f"Using provided coordinates: {latitude}, {longitude}")
    else:
        # Get coordinates for the specified city
        latitude, longitude = get_coordinates(city)

        # If coordinates are not found, use default Amsterdam coordinates
        if latitude is None or longitude is None:
            print(f"Using default coordinates for Amsterdam")
            latitude, longitude = 52.373992, 4.8858433

    # Define the booking steps
    steps = [
        "1. Go to https://www.google.com/maps/search/restaurants/@{latitude},{longitude},14z/data=!3m1!4b1!4m4!2m3!5m1!4e9!6e5 in the browser.",
        "2. Consent any cookie consent popups or similar dialogs that may appear.",
        "3. Make sure the rating filter is set to 4.5 to find top restaurants for {purpose} in the city '{city}' on the map."
    ]
    
    # If restaurant name is provided, add a step to search for it specifically
    if restaurant_name:
        steps.append(f"4. Search for '{restaurant_name}' in the search bar and select it from the results.")
    else:
        steps.append("4. From the resulting restaurant list, select a popular restaurant that seems suitable for {purpose} and click reserve a table.")
    
    # Continue with the rest of the steps
    steps.extend([
        "5. Go to the 'Reserve a table' or something similar section and verify that the booking is free (no prepayment or credit card required).",
        "6. If it is not free or no reservation, go back to the results and repeat step 4 with another random restaurant.",
        "7. set the date to '{date}', the time to '{time}', and the number of people to {party_size}.",
        "8. If the restaurant is fully booked, go back to the results and repeat step 4 with another random restaurant.",
        "9. Fill in the contact information form if required with First name: '{first_name}', Last name: '{last_name}', Email: '{email}', and Phone number: '{phone_number}'.",
        "10. If a special request field or booking description field is available, enter: '{booking_description}'.",
        "11. Proceed to confirm the booking and wait for the booking confirmation to appear.",
        "12. Capture the confirmation details or booking reference.",
        "13. Format the output as a JSON object with the following structure:",
        '''   {{
             "restaurant": {{
               "name": "Restaurant Name",
               "address": "Restaurant Address",
               "phone_number": "Restaurant Phone Number",
               "rating": 4.5,
               "price_range": "$$$",
               "cuisine_type": "Cuisine Type",
               "popular_dishes": ["Dish 1", "Dish 2"],
               "opening_hours": "Opening Hours"
             }},
             "booking": {{
               "confirmation_number": "Confirmation reference if available",
               "date": "{date}",
               "time": "{time}",
               "party_size": {party_size},
               "first_name": "{first_name}",
               "last_name": "{last_name}",
               "special_requests": "{booking_description}",
               "status": "confirmed"
             }},
             "additional_notes": "Any additional relevant information"
           }}'''
    ])
    
    # Modify the steps for test mode
    if test_mode or os.environ.get('TEST_MODE', 'false').lower() == 'true':
        steps = [
            "1. Go to https://www.google.com/maps/search/restaurants/@{latitude},{longitude},14z/data=!3m1!4b1!4m4!2m3!5m1!4e9!6e5 in the browser.",
            "2. Consent any cookie consent popups or similar dialogs that may appear.",
            "3. Make sure the rating filter is set to 4.5 to find top restaurants for {purpose} in the city '{city}' on the map.",
            "4. From the resulting restaurant list, select a popular restaurant that seems suitable for {purpose}.",
            "5. Collect and return detailed information about the selected restaurant including:",
            "   - Restaurant name",
            "   - Address",
            "   - Phone number (if available)",
            "   - Rating",
            "   - Price range",
            "   - Popular dishes or menu highlights (if available)",
            "   - Opening hours for the requested date",
            "6. Format the output as a JSON object with the following structure:",
            '''   {{
                 "restaurant": {{
                   "name": "Restaurant Name",
                   "address": "Restaurant Address",
                   "phone_number": "Restaurant Phone Number",
                   "rating": 4.5,
                   "price_range": "$$$",
                   "cuisine_type": "Cuisine Type",
                   "popular_dishes": ["Dish 1", "Dish 2"],
                   "opening_hours": "Opening Hours"
                 }},
                 "additional_notes": "Any additional information"
               }}''',
            "7. STOP HERE - TEST MODE ACTIVE. Do not proceed with the booking process."
        ]
    
    # Format each step with the user's parameters
    formatted_steps = [step.format(
        city=city,
        date=date,
        time=time,
        party_size=party_size,
        purpose=purpose,
        latitude=latitude,
        longitude=longitude,
        first_name=first_name or "N/A",
        last_name=last_name or "N/A",
        email=email or "N/A",
        phone_number=phone_number or "N/A",
        booking_description=booking_description or "No special requests",
        restaurant_name=restaurant_name or "N/A"
    ) for step in steps]
    
    # Define the restaurant booking task
    booking_task = "\n".join(formatted_steps)
    
    # Initialize controller with output model
    controller = Controller(output_model=BookingResult)
    
    # Initialize and run the agent
    agent = Agent(
        task=booking_task,
        llm=llm,
        browser=browser,
        controller=controller,
        enable_memory=True
    )
    
    try:
        history = await agent.run()
        result = history.final_result()
        if result:
            # Parse the result as a BookingResult
            return result
        else:
            return '{"error": "No result returned from agent"}'
    finally:
        # Ensure browser is closed even if an error occurs
        await browser.close()

async def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Check for test mode from CLI argument or environment variable
    test_mode = args.test or os.environ.get('TEST_MODE', 'false').lower() == 'true'
    
    if test_mode:
        print("Running in TEST MODE - will only collect restaurant information without booking")
    
    # Set default values if not provided
    from datetime import datetime, timedelta

    
    # Default date is tomorrow
    if not args.date:
        tomorrow = datetime.now() + timedelta(days=1)
        date = tomorrow.strftime('%Y-%m-%d')
        print(f"Using default date (tomorrow): {date}")
    else:
        date = args.date
    
    # Default time is 18:00 (6 PM)
    if not args.time:
        time = "18:00"
        print(f"Using default time: {time}")
    else:
        time = args.time
    
    # Default party size is 2
    if not args.party_size:
        party_size = 2
        print(f"Using default party size: {party_size}")
    else:
        party_size = args.party_size
    
    # Execute the restaurant booking
    result = await book_restaurant(
        city=args.city,
        date=date,
        time=time,
        party_size=party_size,
        purpose=args.purpose,
        model=args.model,
        test_mode=test_mode,
        first_name=args.first_name,
        last_name=args.last_name,
        email=args.email,
        phone_number=args.phone_number,
        booking_description=args.booking_description,
        restaurant_name=args.restaurant_name
    )
    
    if test_mode:
        print("Restaurant information retrieved successfully!")
    else:
        print("Booking process completed!")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())