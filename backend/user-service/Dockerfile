# Dockerfile for user-service
FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    libmariadb-dev-compat \
    pkg-config \
    && apt-get clean
WORKDIR /app
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
COPY .env /app/.env
EXPOSE 8000
CMD ["/wait-for-it.sh", "mysql_db:3306", "--timeout=60", "--", "sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
