FROM python:3.13.3-slim-bookworm as base 

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

FROM base as dev

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/app.py"]