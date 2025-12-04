# --- Stage 1: Build React app ---
FROM node:18-alpine AS build
WORKDIR /app

# Copy only package files first (for caching)
COPY package*.json ./

# 🧩 Fix AJV / Webpack / CRACO compatibility
RUN npm install ajv@6.12.6 ajv-keywords@3.5.2 webpack@5.74.0 --legacy-peer-deps

# Install remaining dependencies
RUN npm install --legacy-peer-deps

# Copy app source
COPY . .

# Build React app with backend API URL
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN echo "Building frontend with API URL: $REACT_APP_API_URL"
RUN npm run build

# --- Stage 2: Serve with NGINX ---
FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html

# Optional: send logs to stdout for Portainer visibility
RUN sed -i 's|access_log .*|access_log /dev/stdout;|' /etc/nginx/nginx.conf && \
    sed -i 's|error_log .*|error_log /dev/stderr;|' /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
