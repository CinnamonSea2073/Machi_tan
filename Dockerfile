# Multi-stage build: Build Vue app first
FROM node:20-alpine as vue-builder

WORKDIR /vue-app

# Copy Vue app package files and install dependencies
COPY machi-vue/package*.json ./
RUN npm ci --verbose

# Copy Vue app source and build
COPY machi-vue/ ./
RUN npm run build

# Main Python application
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python application
COPY app/ ./app/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Copy built Vue app from previous stage
COPY --from=vue-builder /vue-app/dist ./machi-vue/dist

ENV PORT=8000
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
