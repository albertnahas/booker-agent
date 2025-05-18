# Booker Agent - Cloud Deployment Guide

This repository contains a restaurant booking agent that uses browser automation and language models to book restaurants automatically.

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key and/or Anthropic API key depending on which model you want to use

### Running with Docker

1. Build and run the container:

```bash
docker-compose up --build
```

This will start the API server on port 8000.

2. To run with custom parameters using the CLI (bypassing the API):

```bash
docker-compose run --entrypoint "python booker.py" booker-agent --city "Paris" --party_size 4 --date "2025-05-20" --time "19:30" --purpose "birthday dinner" --model "gpt-4o"
```

### Environment Variables

Create a `.env` file in the project root with your API keys:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
BROWSER_HEADLESS=true
```

The `BROWSER_HEADLESS` variable controls whether the browser runs in headless mode. For cloud deployments, this should be set to `true`.

## Cloud Deployment

The Docker container is designed to run in any cloud environment that supports Docker containers, such as:

- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Digital Ocean App Platform
- Kubernetes clusters

### Important Notes for Cloud Deployment

1. **Browser Support**: The container includes Chromium browser and all necessary dependencies.

2. **Headless Mode**: The browser is configured to run in headless mode by default in cloud environments.

3. **Memory Requirements**: Ensure your cloud instance has at least 2GB of RAM to handle browser automation and language model operations.

4. **API Keys**: Securely store and provide API keys as environment variables through your cloud provider's secrets management.

5. **Networking**: The container needs outbound internet access to connect to restaurant booking websites and API services.

## API Usage

The application exposes a REST API that allows you to trigger restaurant bookings remotely. Once deployed, you can interact with the API as follows:

### Starting a Booking

To initiate a restaurant booking, send a POST request to the `/book` endpoint:

```bash
curl -X POST "http://your-container-url:8000/book" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Paris",
    "date": "2025-05-20",
    "time": "19:30",
    "party_size": 4,
    "purpose": "birthday dinner",
    "model": "gpt-4o",
    "test_mode": true
  }'
```

Setting `test_mode` to `true` will only collect restaurant information without making an actual booking. This is useful for:
- Testing the system without making real reservations
- Gathering information about restaurants before deciding to book
- Previewing available options without commitment

The response will include a booking ID that you can use to check the status:

```json
{
  "status": "accepted",
  "message": "Booking process started. You can check the status using the booking ID.",
  "booking_id": "booking_20250518123456",
  "details": null
}
```

### Checking Booking Status

To check the status of a booking, send a GET request to the `/status/{booking_id}` endpoint:

```bash
curl "http://your-container-url:8000/status/booking_20250518123456"
```

The response will include the current status of the booking:

```json
{
  "status": "completed",
  "message": "Booking completed",
  "booking_id": "booking_20250518123456",
  "details": {
    "city": "Paris",
    "date": "2025-05-20",
    "time": "19:30",
    "party_size": 4,
    "purpose": "birthday dinner",
    "model": "gpt-4o",
    "test_mode": true,
    "result": "Successful booking at Restaurant XYZ for May 20, 2025 at 19:30..."
  }
}
```

### API Documentation

The API includes automatic Swagger documentation. Access it by navigating to:

```
http://your-container-url:8000/docs
```

This provides an interactive interface for testing the API endpoints.

## Troubleshooting

If you encounter issues with the browser in the container:

1. Check the container logs for any errors related to Chromium.
2. Ensure the cloud instance has sufficient memory and CPU resources.
3. Verify that all required environment variables are properly set.
4. For debugging purposes, you can attach to the running container:

```bash
docker exec -it booker-agent_booker-agent_1 /bin/bash
```
