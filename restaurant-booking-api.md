# Restaurant Booking API Client

This document provides a TypeScript implementation for calling the Restaurant Booking API service. The client uses Axios for HTTP requests.

## Installation

```bash
npm install axios
# or
yarn add axios
```

## TypeScript Interfaces

First, let's define the types that match the server's data models:

```typescript
interface RestaurantDetails {
  name: string;
  address: string;
  phone_number?: string;
  rating?: number;
  price_range?: string;
  cuisine_type?: string;
  popular_dishes?: string[];
  opening_hours?: string;
}

interface BookingDetails {
  confirmation_number?: string;
  date: string;
  time: string;
  party_size: number;
  first_name?: string;
  last_name?: string;
  special_requests?: string;
  status: string;
}

interface BookingResult {
  restaurant: RestaurantDetails;
  booking?: BookingDetails;
  additional_notes?: string;
}

interface BookingParams {
  city?: string;
  date?: string;
  time?: string;
  party_size?: number;
  purpose?: string;
  test_mode?: boolean;
  first_name?: string;
  last_name?: string;
  email?: string;
  phone_number?: string;
  booking_description?: string;
  restaurant_name?: string;
  latitude?: number;
  longitude?: number;
  callback_url?: string;
}
```

## API Client Implementation

```typescript
import axios, { AxiosInstance } from 'axios';

// Define the response model from the API
interface BookingResponse {
  status: string;
  message: string;
  booking_id?: string;
  details?: any;
}

class RestaurantBookingClient {
  private client: AxiosInstance;
  
  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Book a restaurant or get restaurant information in test mode
   * @param params - Booking parameters
   * @returns Promise with booking response containing booking_id
   */
  async bookRestaurant(params: BookingParams = {}): Promise<BookingResponse> {
    try {
      const response = await this.client.post<BookingResponse>('/book', {
        city: params.city || 'Amsterdam',
        date: params.date, // Will default to tomorrow on server if not provided
        time: params.time || '18:00',
        party_size: params.party_size || 2,
        purpose: params.purpose || 'dinner',
        test_mode: params.test_mode || false,
        first_name: params.first_name,
        last_name: params.last_name,
        email: params.email,
        phone_number: params.phone_number,
        booking_description: params.booking_description,
        restaurant_name: params.restaurant_name,
        latitude: params.latitude,
        longitude: params.longitude,
        callback_url: params.callback_url
      });
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', error.response?.data || error.message);
      } else {
        console.error('Unexpected Error:', error);
      }
      throw error;
    }
  }
  
  /**
   * Check the status of a booking by its ID
   * @param bookingId - The ID of the booking to check
   * @returns Promise with booking response
   */
  async checkBookingStatus(bookingId: string): Promise<BookingResponse> {
    try {
      const response = await this.client.get<BookingResponse>(`/status/${bookingId}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error('API Error:', error.response?.data || error.message);
      } else {
        console.error('Unexpected Error:', error);
      }
      throw error;
    }
  }

  /**
   * Fast version with minimal parameters for quick booking
   * @param city - City for restaurant search
   * @param date - Booking date (YYYY-MM-DD)
   * @param time - Booking time (HH:MM)
   * @param party_size - Number of people
   * @param callback_url - Optional URL to receive notification when booking is complete
   * @returns Promise with booking response
   */
  async quickBook(
    city: string = 'Amsterdam',
    date?: string,
    time: string = '18:00',
    party_size: number = 2,
    callback_url?: string
  ): Promise<BookingResponse> {
    return this.bookRestaurant({
      city,
      date,
      time,
      party_size,
      callback_url
    });
  }

  /**
   * Test mode version that only retrieves restaurant information without booking
   * @param city - City for restaurant search
   * @param restaurant_name - Optional specific restaurant to search for
   * @param callback_url - Optional URL to receive notification when search is complete
   * @returns Promise with booking response
   */
  async findRestaurant(
    city: string = 'Amsterdam',
    restaurant_name?: string,
    callback_url?: string
  ): Promise<BookingResponse> {
    return this.bookRestaurant({
      city,
      restaurant_name,
      test_mode: true,
      callback_url
    });
  }
}

export default RestaurantBookingClient;
```

## Usage Examples

### Basic Booking

```typescript
import RestaurantBookingClient from './restaurant-booking-client';

const api = new RestaurantBookingClient();

// Quick booking with minimal parameters
async function makeSimpleBooking() {
  try {
    // Will use defaults for most parameters (Amsterdam, tomorrow, 18:00, 2 people)
    const response = await api.quickBook();
    console.log('Booking initiated:', response);
    
    // Check status later using the booking ID
    if (response.booking_id) {
      // Poll for status until completed
      const checkInterval = setInterval(async () => {
        const status = await api.checkBookingStatus(response.booking_id!);
        console.log('Booking status:', status.status);
        
        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(checkInterval);
          console.log('Final booking result:', status.details?.result);
        }
      }, 10000); // Check every 10 seconds
    }
  } catch (error) {
    console.error('Booking failed:', error);
  }
}

// Booking with all parameters
async function makeDetailedBooking() {
  try {
    const callbackUrl = 'https://your-server.com/webhook/booking-complete';
    const response = await api.bookRestaurant({
      city: 'Paris',
      date: '2025-05-20',
      time: '19:30',
      party_size: 4,
      purpose: 'anniversary dinner',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      phone_number: '+123456789',
      booking_description: 'Window seat preferred',
      restaurant_name: 'Le Bistro',
      callback_url: callbackUrl // The result will be sent here when ready
    });
    console.log('Booking initiated:', response);
  } catch (error) {
    console.error('Booking failed:', error);
  }
}

// Just find a restaurant without booking (test mode)
async function findRestaurantInfo() {
  try {
    // You can provide a callback URL to get the complete results when ready
    const callbackUrl = 'https://your-server.com/webhook/restaurant-info';
    const response = await api.findRestaurant('Barcelona', 'La Taperia', callbackUrl);
    console.log('Restaurant search initiated:', response);
    
    // If you didn't provide a callback URL, you can poll for results
    if (response.booking_id) {
      setTimeout(async () => {
        const status = await api.checkBookingStatus(response.booking_id!);
        if (status.status === 'completed') {
          console.log('Restaurant found:', status.details?.result.restaurant);
        }
      }, 30000); // Check after 30 seconds
    }
  } catch (error) {
    console.error('Restaurant search failed:', error);
  }
}
```

## Error Handling

The client includes basic error handling that logs error messages and rethrows the error for further handling. You can extend this with your own error handling logic as needed.

## Environment Configuration

You may want to configure the API base URL through environment variables:

```typescript
// Using environment variables
const API_BASE_URL = process.env.RESTAURANT_API_URL || 'http://localhost:8000';
const api = new RestaurantBookingClient(API_BASE_URL);
```

## Using Webhooks with Callbacks

The API supports callbacks via webhooks, which allows you to receive booking results asynchronously once the booking process completes. This is especially useful since restaurant bookings may take some time to complete.

### Setting Up a Webhook Endpoint

You need to set up an HTTP endpoint that can receive POST requests. The API will send a JSON payload to this endpoint when the booking process completes:

```typescript
// Example Express.js webhook endpoint
import express from 'express';
const app = express();
app.use(express.json());

app.post('/webhook/booking-complete', (req, res) => {
  const bookingData = req.body;
  
  console.log('Booking completed:', bookingData);
  
  // Process the booking data
  // bookingData will contain the same structure as the BookingResponse 
  // with additional details including the complete restaurant and booking information
  
  // Send a 200 OK response to acknowledge receipt
  res.status(200).send('Webhook received');
});

app.listen(3000, () => {
  console.log('Webhook server running on port 3000');
});
```

### Making a Request with Callback URL

```typescript
import RestaurantBookingClient from './restaurant-booking-client';

const api = new RestaurantBookingClient();

async function bookWithCallback() {
  try {
    // The webhook URL that will receive the booking result
    const callbackUrl = 'https://your-server.com/webhook/booking-complete';
    
    // Make the booking request
    const response = await api.bookRestaurant({
      city: 'Paris',
      date: '2025-05-20',
      time: '19:30',
      party_size: 4,
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      callback_url: callbackUrl // This is where the result will be sent when ready
    });
    
    // The initial response only contains the booking_id and status
    console.log('Booking initiated:', response);
    console.log('Booking ID:', response.booking_id);
    
    // You can use the booking ID to poll for status if needed
    // But the webhook will be called automatically when complete
  } catch (error) {
    console.error('Failed to initiate booking:', error);
  }
}

// You can also check the status manually using the booking ID
async function checkStatus(bookingId: string) {
  try {
    const status = await api.checkBookingStatus(bookingId);
    console.log('Current booking status:', status);
  } catch (error) {
    console.error('Failed to check booking status:', error);
  }
}
```

### Webhook Payload Structure

The webhook payload will contain the full booking details:

```typescript
{
  "status": "completed", // or "failed"
  "message": "Booking process completed",
  "booking_id": "booking_20250518123456",
  "details": {
    // All the original request parameters
    "city": "Paris",
    "date": "2025-05-20",
    "time": "19:30",
    // ...
    
    // Plus the result data
    "result": {
      "restaurant": {
        "name": "Le Bistro",
        "address": "123 Champs-Élysées, Paris",
        "phone_number": "+33123456789",
        "rating": 4.7,
        "price_range": "$$$",
        "cuisine_type": "French",
        "popular_dishes": ["Coq au Vin", "Beef Bourguignon"],
        "opening_hours": "17:00-23:00"
      },
      "booking": {
        "confirmation_number": "LB12345",
        "date": "2025-05-20",
        "time": "19:30",
        "party_size": 4,
        "first_name": "John",
        "last_name": "Doe",
        "special_requests": null,
        "status": "confirmed"
      },
      "additional_notes": "Reservation confirmed via Google Maps"
    }
  }
}
```
