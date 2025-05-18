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
}
```

## API Client Implementation

```typescript
import axios, { AxiosInstance } from 'axios';

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
   * @returns Promise with booking result
   */
  async bookRestaurant(params: BookingParams = {}): Promise<BookingResult> {
    try {
      const response = await this.client.post<BookingResult>('/book-restaurant', {
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
        longitude: params.longitude
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
   * Fast version with minimal parameters for quick booking
   * @param city - City for restaurant search
   * @param date - Booking date (YYYY-MM-DD)
   * @param time - Booking time (HH:MM)
   * @param party_size - Number of people
   * @returns Promise with booking result
   */
  async quickBook(
    city: string = 'Amsterdam',
    date?: string,
    time: string = '18:00',
    party_size: number = 2
  ): Promise<BookingResult> {
    return this.bookRestaurant({
      city,
      date,
      time,
      party_size
    });
  }

  /**
   * Test mode version that only retrieves restaurant information without booking
   * @param city - City for restaurant search
   * @param restaurant_name - Optional specific restaurant to search for
   * @returns Promise with restaurant details
   */
  async findRestaurant(
    city: string = 'Amsterdam',
    restaurant_name?: string
  ): Promise<BookingResult> {
    return this.bookRestaurant({
      city,
      restaurant_name,
      test_mode: true
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
    const result = await api.quickBook();
    console.log('Booking successful:', result);
  } catch (error) {
    console.error('Booking failed:', error);
  }
}

// Booking with all parameters
async function makeDetailedBooking() {
  try {
    const result = await api.bookRestaurant({
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
      restaurant_name: 'Le Bistro'
    });
    console.log('Booking successful:', result);
  } catch (error) {
    console.error('Booking failed:', error);
  }
}

// Just find a restaurant without booking (test mode)
async function findRestaurantInfo() {
  try {
    const result = await api.findRestaurant('Barcelona', 'La Taperia');
    console.log('Restaurant found:', result.restaurant);
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
