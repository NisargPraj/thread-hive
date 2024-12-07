# Dockerfile for post-service
FROM python:3.9-slim
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
