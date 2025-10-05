# syntax=docker/dockerfile:1.4

FROM node:18-alpine AS builder

LABEL stage=builder

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci --only=production \
    && npm cache clean --force

COPY . .

ARG VITE_API_URL=http://localhost:8000
ARG NODE_ENV=production

RUN npm run build

FROM nginx:1.25-alpine AS runtime

LABEL maintainer="security@saascafeterias.com"
LABEL version="1.0.0"

RUN apk add --no-cache curl

RUN rm /etc/nginx/conf.d/default.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

COPY --from=builder --chown=nginx:nginx /build/dist /usr/share/nginx/html

RUN addgroup -g 1000 -S appgroup || true \
    && adduser -u 1000 -S appuser -G appgroup || true \
    && chown -R appuser:appgroup /usr/share/nginx/html \
    && chown -R appuser:appgroup /var/cache/nginx \
    && chown -R appuser:appgroup /var/log/nginx \
    && chown -R appuser:appgroup /etc/nginx/conf.d \
    && touch /var/run/nginx.pid \
    && chown -R appuser:appgroup /var/run/nginx.pid

USER appuser

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

CMD ["nginx", "-g", "daemon off;"]