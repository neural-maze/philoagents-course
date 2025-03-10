FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Build the application
RUN npm run build

# Expose port 8080 (matches webpack dev server port)
EXPOSE 8080

# Start the development server
CMD ["npm", "run", "dev"]