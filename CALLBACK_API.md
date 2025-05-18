# Restaurant Booking Callback API

This document explains how to use the callback URL feature of the Restaurant Booking API. The callback mechanism allows your application to receive an asynchronous notification when a booking operation is completed, without having to poll the API for status updates.

## Callback URL Parameter

When making a booking request, you can include a `callback_url` parameter to specify where the API should send the results once the booking operation is completed.

```json
{
  "city": "Amsterdam",
  "time": "18:00",
  "party_size": 2,
  "callback_url": "https://your-server.com/api/callbacks/booking"
}
```

## Callback Data Format

When the booking operation is completed (either successfully or with an error), the API will send a POST request to the specified callback URL with a JSON payload in the following format:

```json
{
  "status": "completed", // or "failed"
  "message": "Booking completed", // or error message
  "booking_id": "booking_20250518123456",
  "details": {
    // Original request parameters
    "city": "Amsterdam",
    "date": "2025-05-19",
    "time": "18:00",
    // ... other request parameters
    
    // Result details (if successful)
    "result": {
      "restaurant": {
        "name": "Restaurant Name",
        "address": "Restaurant Address",
        "phone_number": "Restaurant Phone Number",
        "rating": 4.5,
        "price_range": "$$$",
        "cuisine_type": "Cuisine Type",
        "popular_dishes": ["Dish 1", "Dish 2"],
        "opening_hours": "Opening Hours"
      },
      "booking": {
        "confirmation_number": "ABC123",
        "date": "2025-05-19",
        "time": "18:00",
        "party_size": 2,
        "first_name": "John",
        "last_name": "Doe",
        "special_requests": "Window seat preferred",
        "status": "confirmed"
      },
      "additional_notes": "Any additional relevant information"
    }
  }
}
```

## Callback Error Handling

Your callback endpoint should respond with a 2xx HTTP status code to acknowledge receipt of the callback. If the callback fails (e.g., your server is down or returns a non-2xx status code), the API will log the error but will not retry the callback.

The booking result will still be available through the regular `/status/{booking_id}` endpoint even if the callback fails.

## TypeScript/JavaScript Client Implementation

Here's a TypeScript implementation for a client that uses the callback URL feature:

```typescript
import axios, { AxiosInstance } from 'axios';

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
   * Book a restaurant with callback notification
   * @param params - Booking parameters including callback_url
   * @returns Promise with booking initiation response
   */
  async bookRestaurantWithCallback(params: BookingParams & { callback_url: string }) {
    try {
      const response = await this.client.post('/book', {
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
}

// Usage example:
const client = new RestaurantBookingClient('https://your-booking-api.com');
client.bookRestaurantWithCallback({
  city: 'Amsterdam',
  date: '2025-05-20',
  time: '19:00',
  party_size: 4,
  first_name: 'Jane',
  last_name: 'Smith',
  email: 'jane.smith@example.com',
  callback_url: 'https://your-app.com/api/booking-callbacks'
});
```

## Setting Up a Callback Endpoint

You'll need to set up an endpoint on your server to receive the callbacks. Here's a simple example using Express.js:

```javascript
const express = require('express');
const app = express();
app.use(express.json());

app.post('/api/booking-callbacks', (req, res) => {
  const bookingResult = req.body;
  console.log('Received booking callback:', bookingResult);
  
  // Process the booking result
  // For example, save to database, notify users, etc.
  
  // Acknowledge receipt of the callback
  res.status(200).send({ received: true });
});

app.listen(3000, () => {
  console.log('Callback server listening on port 3000');
});
```

## Security Considerations

- Ensure your callback endpoint is properly secured, especially if you're handling sensitive information.
- Consider using HTTPS for your callback URL.
- If needed, implement authentication for the callback endpoint to verify the source of the callback.
- You may want to implement a signature verification mechanism to ensure the callback is coming from your booking service.
