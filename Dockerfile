# Use the distroless base image
FROM gcr.io/distroless/python3-debian11

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set the entrypoint
ENTRYPOINT ["python", "ratio.py"]
