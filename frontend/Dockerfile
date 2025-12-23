FROM node:18-alpine

WORKDIR /app

# Copy package files first (for layer caching)
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run development server
CMD ["npm", "run", "dev", "--", "--host"]
