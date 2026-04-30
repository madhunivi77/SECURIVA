# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci || npm install

COPY . .
RUN npm run build

# Serve stage
FROM nginx:alpine

RUN apk add --no-cache gettext

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY docker-entrypoint.sh /docker-entrypoint.d/40-render-backend-url.sh
RUN chmod +x /docker-entrypoint.d/40-render-backend-url.sh

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
