# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script and CSV file
COPY app.py .
COPY tickers.csv .

# Set default entrypoint to python
ENTRYPOINT ["python", "app.py"]