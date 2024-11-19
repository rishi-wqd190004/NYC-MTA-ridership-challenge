# Use the official Python image from Docker Hub
FROM python:slim-bookworm

# Set the working directory in the container
WORKDIR /app/src

# Install dependencies for Chromium and other system libraries
RUN apt-get update && apt-get install -y \
    chromium \
    libglib2.0-0 \
    libnss3 \
    libxss1 \
    libgdk-pixbuf2.0-0 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY src/requirements.txt /app/src

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY src /app/src

# Copy the dataset into the container
COPY dataset/MTA_Daily_Ridership.csv /app/data/MTA_Daily_Ridership.csv

# Expose the port the app will run on
EXPOSE 8050

# Set the environment variable to point to the Chromium binary
ENV BROWSER_PATH=/usr/bin/chromium

# Define the command to run the app
CMD ["python", "app.py"]
