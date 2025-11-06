FROM python:3.11-slim as builder 

ENV EVENTLET_NO_GREENDNS=yes

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt
FROM python:3.11-slim
COPY --from=builder /install /usr/local
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app
COPY . .
USER appuser

CMD ["python", "src.main.py"]