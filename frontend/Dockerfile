# Frontend Dockerfile - Node.js serving mode
FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 80
# Use vite preview to serve the built files and handle proxying
CMD ["npm", "run", "preview"]
