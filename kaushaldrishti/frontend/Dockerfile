FROM node:20-alpine

WORKDIR /app

# Dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Application code
COPY . .

EXPOSE 3000

# Development server
CMD ["npm", "run", "dev"]
