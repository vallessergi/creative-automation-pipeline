FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies
COPY package.json vite.config.js ./
RUN npm install

# Copy source and build
COPY index.html ./
COPY src ./src
RUN npm run build

# ---- Stage 2: Serve with nginx ----
FROM nginx:alpine

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy build output from previous stage
COPY --from=build /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Default command
CMD ["nginx", "-g", "daemon off;"]