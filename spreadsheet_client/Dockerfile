FROM node:20.19-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*
COPY package*.json ./
RUN npm cache clean --force
RUN rm -rf node_modules
RUN npm install --force
RUN npm install -g @rollup/rollup-linux-x64-gnu
FROM node:20.19-slim AS dev
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY . .
ENV HOST=0.0.0.0
ENV PORT=3000
EXPOSE 3000
CMD ["npm", "run", "dev"]