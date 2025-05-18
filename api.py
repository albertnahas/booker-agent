import os
import argparse
import asyncio
import aiohttp
import logging
from typing import Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl
import uvicorn
from booker import book_restaurant

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create FastAPI app
app = FastAPI(title="Restaurant Booking API", 
              description="API for automated restaurant booking using AI",
              version="1.0.0")

# Define the request model
class BookingRequest(BaseModel):
    city: str = "Amsterdam"
    date: Optional[str] = None
    time: str = "18:00"
    party_size: int = 2
    purpose: str = "dinner"
    model: str = "gpt-4.1"
    test_mode: bool = False
    # Contact information fields
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    booking_description: Optional[str] = None
    restaurant_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Callback URL for webhook notifications
    callback_url: Optional[HttpUrl] = None

# Define the response model
class BookingResponse(BaseModel):
    status: str
    message: str
    booking_id: Optional[str] = None
    details: Optional[dict] = None

# Global store for booking results
booking_results = {}

@app.get("/")
async def root():
    return {"status": "ok", "message": "Restaurant Booking API is running"}

@app.post("/book", response_model=BookingResponse)
async def create_booking(request: BookingRequest, background_tasks: BackgroundTasks):
    # Generate a booking ID
    booking_id = f"booking_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Set default date to tomorrow if not provided
    if not request.date:
        tomorrow = datetime.now() + timedelta(days=1)
        request.date = tomorrow.strftime('%Y-%m-%d')
    
    # Store initial status
    booking_results[booking_id] = {
        "status": "pending",
        "message": f"{'Test mode - Restaurant information retrieval' if request.test_mode else 'Booking process'} started",
        "details": request.dict()
    }
    
    # Run the booking process in the background
    background_tasks.add_task(
        process_booking, 
        booking_id=booking_id,
        city=request.city,
        date=request.date,
        time=request.time,
        party_size=request.party_size,
        purpose=request.purpose,
        model=request.model,
        test_mode=request.test_mode,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone_number=request.phone_number,
        booking_description=request.booking_description,
        restaurant_name=request.restaurant_name,
        latitude=request.latitude,
        longitude=request.longitude,
        callback_url=request.callback_url
    )
    
    return BookingResponse(
        status="accepted",
        message=f"{'Test mode - Restaurant information retrieval' if request.test_mode else 'Booking process'} started. You can check the status using the booking ID.",
        booking_id=booking_id
    )

@app.get("/status/{booking_id}", response_model=BookingResponse)
async def get_booking_status(booking_id: str):
    if booking_id not in booking_results:
        raise HTTPException(status_code=404, detail="Booking ID not found")
    
    result = booking_results[booking_id]
    
    return BookingResponse(
        status=result["status"],
        message=result["message"],
        booking_id=booking_id,
        details=result["details"]
    )

async def send_callback(callback_url: str, data: dict):
    """
    Send booking results to the provided callback URL.
    
    Args:
        callback_url: The URL to send the callback to
        data: The data to send in the callback
    """
    if not callback_url:
        return
        
    try:
        logging.info(f"Sending callback to {callback_url}")
        async with aiohttp.ClientSession() as session:
            async with session.post(callback_url, json=data) as response:
                if response.status >= 400:
                    logging.error(f"Callback to {callback_url} failed with status {response.status}")
                else:
                    logging.info(f"Callback to {callback_url} succeeded with status {response.status}")
    except Exception as e:
        logging.error(f"Error sending callback to {callback_url}: {str(e)}")

async def process_booking(booking_id: str, **kwargs):
    try:
        # Update status to processing
        test_mode = kwargs.get('test_mode', False)
        callback_url = kwargs.get('callback_url')
        operation_type = "Restaurant information retrieval" if test_mode else "Booking"
        
        booking_results[booking_id]["status"] = "processing"
        booking_results[booking_id]["message"] = f"{operation_type} in progress..."
        
        # Call the actual booking function
        result = await book_restaurant(**kwargs)
        
        # Update with results
        booking_results[booking_id]["status"] = "completed"
        booking_results[booking_id]["message"] = f"{operation_type} completed"
        booking_results[booking_id]["details"]["result"] = result
        
        # Send callback if URL was provided
        if callback_url:
            callback_data = {
                "status": "completed",
                "message": f"{operation_type} completed",
                "booking_id": booking_id,
                "details": booking_results[booking_id]["details"]
            }
            await send_callback(callback_url, callback_data)
        
    except Exception as e:
        # Handle errors
        booking_results[booking_id]["status"] = "failed"
        booking_results[booking_id]["message"] = f"Operation failed: {str(e)}"
        
        # Send error callback if URL was provided
        if callback_url:
            callback_data = {
                "status": "failed",
                "message": f"Operation failed: {str(e)}",
                "booking_id": booking_id,
                "details": booking_results[booking_id]["details"]
            }
            await send_callback(callback_url, callback_data)

if __name__ == "__main__":
    # Run the API server
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
