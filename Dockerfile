# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables to ensure Python behaves consistently
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright with Firefox browser only
RUN playwright install --with-deps

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
