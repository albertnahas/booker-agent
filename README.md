# Restaurant Booking Agent

An automated agent for booking restaurant reservations using browser automation and LLMs.

## Features

- Automated restaurant booking through Google Maps
- Supports various cities with geocoding
- Flexible date, time, and party size options
- Test mode to simulate the booking process without confirming
- Support for multiple LLM providers (OpenAI and Anthropic)
- RESTful API with webhook callbacks for asynchronous notifications

## Prerequisites

- Python 3.12 or higher
- OpenAI API key or Anthropic API key
- Internet connection for geocoding and accessing booking platforms

## Setup

1. Ensure you have a virtual environment activated:

   ```
   uv venv
   source .venv/bin/activate  # On Unix/Mac
   ```

2. Install required packages:

   ```
   uv pip install -r requirements.txt
   playwright install
   ```

3. Create a `.env` file based on the `.env.example` with your API keys:

   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # or
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

Run the booking agent with default settings (Amsterdam, tomorrow at 6 PM, party of 2):

```bash
python booker.py
```

### Command Line Options

```
python booker.py [OPTIONS]
```

Available options:

- `--city`: City for restaurant search (default: Amsterdam)
- `--date`: Booking date in YYYY-MM-DD format (default: tomorrow)
- `--time`: Booking time in HH:MM format (default: 18:00)
- `--party_size`: Number of people (default: 2)
- `--purpose`: Purpose of the reservation (default: dinner)
- `--model`: LLM model to use: 'claude-3-5-sonnet-latest' or 'gpt-4.1' (default: gpt-4.1)
- `--test`: Run in test mode without confirming the booking

### Examples

Book a dinner for 4 people in Paris next Friday at 8 PM:

```bash
python booker.py --city "Paris" --date "2025-05-23" --time "20:00" --party_size 4
```

Run in test mode (no actual booking confirmation):

```bash
python booker.py --city "Amsterdam" --test
```

Use Claude instead of GPT:

```bash
python booker.py --model claude-3-5-sonnet-latest
```

## API Usage

The project includes a RESTful API for making bookings programmatically. Start the API server with:

```bash
python api.py
```

This will start the API server on port 8000. You can then use the API to make bookings.

### API Endpoints

- `GET /`: API health check
- `POST /book`: Start a booking process
- `GET /status/{booking_id}`: Check the status of a booking

### Webhook Callbacks

The API supports webhook callbacks to notify your application when a booking is completed. To use this feature:

1. Include a `callback_url` parameter in your booking request
2. When the booking is completed, the API will send a POST request to your callback URL with the booking results

Example:

```bash
python client.py --api-url http://localhost:8000 --city "Amsterdam" --callback-url "https://your-server.com/webhook"
```

For detailed information about the callback feature, see [CALLBACK_API.md](CALLBACK_API.md).

## How It Works

The agent performs the following steps:
1. Converts the city name to coordinates using geocoding
2. Opens Google Maps and searches for highly-rated restaurants
3. Navigates through the booking process
4. Selects date, time, and party size
5. Confirms the booking (unless in test mode)
6. Returns the booking confirmation details

## Debugging

You can enable more verbose logging by adjusting the environment variables in your `.env` file:

```
LOG_LEVEL=INFO
BROWSER_USE_LOGGING_LEVEL=INFO
```
