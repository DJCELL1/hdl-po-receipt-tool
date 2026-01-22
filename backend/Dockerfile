FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Production stage
FROM node:20-alpine

# Install Tesseract OCR
RUN apk add --no-cache tesseract-ocr tesseract-ocr-data-eng

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production

# Copy built files from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/src/database/schema.sql ./dist/database/schema.sql

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 3001

# Run migrations and start server
CMD ["sh", "-c", "npm run migrate && npm start"]
