FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    firefox-esr \
    xvfb \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libcups2 \
    libxss1 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    dbus \
    fontconfig \
    wget \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install playwright and its dependencies
RUN pip install --no-cache-dir playwright==1.41.1 \
    && playwright install firefox --with-deps

# Copy the entrypoint script first and set permissions
COPY entrypoint.sh /app/
RUN dos2unix /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Copy the rest of the application
COPY . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/logs /app/media /app/staticfiles && \
    chmod 777 /app/logs /app/media /app/staticfiles

ENV STATIC_ROOT /static
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "software.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]