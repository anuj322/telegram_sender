FROM python:3.13-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create sessions directory with proper permissions
RUN mkdir -p /app/sessions && chmod 755 /app/sessions

# Expose app port
EXPOSE 5000

# Run Flask app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
