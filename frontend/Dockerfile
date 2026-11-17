# ==============================================================================
# AegisRansom-X React SOC Dashboard Dockerfile (Multi-stage build)
# ==============================================================================

# Stage 1: Build React + Vite TypeScript production bundle
FROM node:22-alpine AS builder
WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code and build assets
COPY . .
RUN npm run build

# Stage 2: Serve production assets via lightweight Nginx
FROM nginx:alpine AS runner

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built distribution from Stage 1
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx proxy config bridging host backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
