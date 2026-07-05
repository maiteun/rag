FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ARG VITE_DATA_MODE=api
ARG VITE_API_BASE_URL=/api
ARG VITE_USER_ID=00000000-0000-0000-0000-000000000001
ENV VITE_DATA_MODE=$VITE_DATA_MODE
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_USER_ID=$VITE_USER_ID
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
