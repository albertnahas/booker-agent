# Restaurant Booking Agent Setup Guide

This guide provides instructions for setting up the Restaurant Booking Agent on your machine.

## Prerequisites

- Python 3.12 or higher
- Anthropic API key or OpenAI API key
- Internet connection for geocoding and accessing booking platforms

## Setup

1. Create and activate a virtual environment:

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

## Environment Configuration

The following environment variables can be configured:

- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`: API key for the LLM provider
- `LOG_LEVEL`: Logging level (default: CRITICAL)
- `BROWSER_USE_LOGGING_LEVEL`: Browser logging level (default: CRITICAL)
- `TEST_MODE`: Set to 'true' to run in test mode without confirming bookings

## Available Parameters

The booking agent accepts the following parameters:

1. `city`: City to search for restaurants (default: Amsterdam)
2. `date`: Booking date in YYYY-MM-DD format (default: tomorrow)
3. `time`: Booking time in HH:MM format (default: 18:00)
4. `party_size`: Number of people (default: 2)
5. `purpose`: Purpose of the reservation (default: dinner)
6. `model`: LLM model to use ('claude-3-5-sonnet-latest' or 'gpt-4.1')
7. `test_mode`: Whether to run in test mode without confirming booking

## Example Usage

```bash
# Book a dinner for 2 in Amsterdam tomorrow at 6 PM
python booker.py

# Book a lunch for 3 in Paris on a specific date
python booker.py --city "Paris" --date "2025-05-25" --time "12:30" --party_size 3 --purpose "lunch"

# Run in test mode with Claude model
python booker.py --model claude-3-5-sonnet-latest --test
```

## Troubleshooting

If you encounter issues:

1. Make sure the browser automation package is installed correctly with `playwright install`
2. Verify that your API key is valid and properly set in the `.env` file
3. Check that the geocoding service is working for your selected city
4. Try adjusting the log levels in the `.env` file for more information
5. Run in test mode first to verify everything works before making actual bookings
