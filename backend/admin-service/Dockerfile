# Dockerfile for admin-service
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies required for mysqlclient and wait-for-it script
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

# Make wait-for-it.sh executable
RUN chmod +x wait-for-it.sh

EXPOSE 8000

# Wait for MySQL to be ready before starting Django
CMD ["./wait-for-it.sh", "mysql_db:3306", "--", "python", "manage.py", "runserver", "0.0.0.0:8000"]
