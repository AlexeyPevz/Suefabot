# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx config if exists
COPY nginx.conf /etc/nginx/conf.d/default.conf 2>/dev/null || :

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]