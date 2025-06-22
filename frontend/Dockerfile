# Stage 1: Build the React application
FROM node:20 AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
# Copy package.json and package-lock.json for dependency installation
COPY package.json package-lock.json ./

# Install dependencies
# This layer is cached and will only be re-run if package.json or package-lock.json change
RUN npm install

# Copy the rest of the application's code
# This layer is invalidated when any of the source files change
COPY . .

# Build the application for production
RUN npm run build

# Stage 2: Serve the application using Nginx
FROM nginx:stable-alpine

# Copy the build output from the previous stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]