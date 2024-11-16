# Use the official Python image from Docker Hub
FROM python:slim-bookworm

# Set the working directory in the container
WORKDIR /src

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose the port the app will run on
EXPOSE 8050

# Define the command to run the app
CMD ["python", "app.py"]