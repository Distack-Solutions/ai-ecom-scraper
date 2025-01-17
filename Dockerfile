# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables to ensure Python behaves consistently
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies for Playwright and Python
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    unzip \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libxdamage1 \
    libxkbcommon0 \
    libwayland-client0 \
    libwayland-server0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Firefox
RUN pip install --no-cache-dir playwright && playwright install firefox

# Copy the entire Django project into the container
COPY . /app/

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Set static files directory
ENV STATIC_ROOT /static

# Expose the port Django runs on (default: 8000)
EXPOSE 8000

# Run the Django application using Gunicorn
CMD ["gunicorn", "software.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
