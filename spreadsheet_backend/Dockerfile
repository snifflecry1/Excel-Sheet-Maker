FROM python:3.13-slim as builder 

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.13-slim
COPY --from=builder /install /usr/local
WORKDIR /app
COPY . .

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000", "--reload"]