# ---------- Stage 1: build Next.js static export ----------
FROM node:20-alpine AS web
WORKDIR /web
COPY apps/web/package.json ./
RUN npm install
COPY apps/web ./
RUN npm run build
# -> /web/out

# ---------- Stage 2: Python agent + static frontend ----------
FROM python:3.12-slim
WORKDIR /app
COPY apps/agent/requirements.txt .
RUN pip install --no-cache-dir --retries 10 --timeout 120 -r requirements.txt
COPY apps/agent ./
# bundle the built frontend into /app/static (served at "/" by main.py)
COPY --from=web /web/out ./static
EXPOSE 8080
CMD ["python", "main.py"]
