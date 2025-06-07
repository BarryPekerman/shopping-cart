# Stage 1: build deps
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Stage 2: runtime
FROM python:3.12-slim

RUN useradd -m nonroot
USER nonroot
WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

CMD ["python", "-m", "app.app"]

