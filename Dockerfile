FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including chromium and required packages for browser automation
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    unzip \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    fonts-noto \
    fonts-noto-cjk \
    libu2f-udev \
    libvulkan1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium browser
RUN apt-get update && apt-get install -y chromium \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script to install Playwright browsers
COPY install_browsers.sh .
RUN chmod +x install_browsers.sh
RUN ./install_browsers.sh

# Set environment variables for headless browser
ENV PYTHONUNBUFFERED=1
ENV BROWSER_HEADLESS=true
ENV DISPLAY=:99

# Copy application code
COPY . .

# Expose the API port
EXPOSE 8000

# Command to run the API by default
CMD ["python", "api.py"]
