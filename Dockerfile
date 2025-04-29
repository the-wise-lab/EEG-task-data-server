# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Set the working directory in the container
WORKDIR /app

# Copy all code to the working directory first
COPY . .

# Ensure config file is properly copied
COPY config.yml /app/config.yml

# Install dependencies (now with all code available)
RUN pip install --no-cache-dir -e .

# Create data and logs directories with appropriate permissions
RUN mkdir -p /app/data /app/logs && \
    chmod -R 755 /app/data /app/logs

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["local-data-storage"]