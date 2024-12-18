FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Встановлюємо supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

EXPOSE 3000
EXPOSE 5000

CMD ["supervisord", "-c", "/app/supervisord.conf"]
