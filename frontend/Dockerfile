# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application for production
# Ensure we have VITE_API_URL set to something relative or specific
# For Docker setup we assume the backend is available at /api 
# if we set up nginx reverse proxy, but here let's assume standard Vite build
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the built assets from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80 || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
