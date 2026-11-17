# ==============================================================================
# AegisRansom-X React SOC Dashboard (Root Dockerfile)
# ==============================================================================
FROM node:22-alpine AS builder
WORKDIR /app

# Copy frontend source manifests
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend codebase and build assets
COPY frontend/ ./
RUN npm run build

# Stage 2: Nginx lightweight reverse proxy runner
FROM nginx:alpine AS runner
RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
