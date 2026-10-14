FROM node:22-alpine AS ui
WORKDIR /ui
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
FROM node:22-alpine
WORKDIR /app
COPY invoice/package*.json ./
RUN npm ci --omit=dev
COPY invoice/server.js ./
COPY --from=ui /ui/dist ./public
ENV NODE_ENV=production
USER node
EXPOSE 8081
CMD ["node", "server.js"]
