# Frontend Dockerfile
FROM node:20-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
# Add default nginx config to handle SPA routing if needed
RUN echo 'server { \
    listen 80; \
    listen 443 ssl; \
    server_name localhost; \
    \
    ssl_certificate /etc/nginx/certs/nginx-selfsigned.crt; \
    ssl_certificate_key /etc/nginx/certs/nginx-selfsigned.key; \
    \
    # Increased client_max_body_size for document uploads \
    client_max_body_size 20M; \
    \
    location /flashcards/api/ { \
        proxy_pass http://backend:8000/api/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    location /flashcards/docs { \
        proxy_pass http://backend:8000/docs; \
        proxy_set_header Host $host; \
    } \
    \
    location /flashcards/redoc { \
        proxy_pass http://backend:8000/redoc; \
        proxy_set_header Host $host; \
    } \
    \
    location /flashcards/openapi.json { \
        proxy_pass http://backend:8000/openapi.json; \
        proxy_set_header Host $host; \
    } \
    \
    location /flashcards/ { \
        alias /usr/share/nginx/html/; \
        index index.html; \
        try_files $uri $uri/ /flashcards/index.html; \
    } \
    \
    location / { \
        return 301 /flashcards/; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
