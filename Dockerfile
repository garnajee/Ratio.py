FROM python:3.11-slim-bookworm AS builder

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Use the distroless base image
FROM gcr.io/distroless/python3-debian12

WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application code
COPY . .

# Set the entrypoint
ENTRYPOINT ["python3", "ratio.py"]
