FROM node:18-alpine AS build

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm ci

COPY . .

RUN npm run build

# Serve stage
FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

ENV BACKEND_URL=http://backend:8080

ENTRYPOINT ["/entrypoint.sh"]
