# Vulnerable React Server - FOR TESTING ONLY
# DO NOT DEPLOY TO PRODUCTION

FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application files
COPY . .

# Build React frontend
RUN npm run build

# Expose port
EXPOSE 3000

# Warning message
RUN echo "WARNING: This container contains intentionally vulnerable software!" > /etc/motd

# Start the server
CMD ["npm", "start"]

# Labels
LABEL maintainer="Security Testing"
LABEL description="Intentionally vulnerable React server for security testing"
LABEL warning="DO NOT DEPLOY TO PRODUCTION - FOR TESTING ONLY"
