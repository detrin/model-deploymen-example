FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info", "--pool=prefork", "--concurrency=1", "--max-tasks-per-child=100"]