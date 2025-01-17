# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables to ensure Python behaves consistently
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libxkbcommon0 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libfontconfig1 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libxshmfence1 \
    libcairo-gobject2 \
    libgdk-pixbuf2.0-0 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright with Firefox browser only
RUN playwright install firefox --with-deps

# Copy the entire Django project into the container
COPY . /app/

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

ENV STATIC_ROOT /static

# Expose the port Django runs on (default: 8000)
EXPOSE 8000

# Run the Django development server
CMD ["gunicorn", "software.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
