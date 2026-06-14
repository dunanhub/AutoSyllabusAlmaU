FROM node:20-alpine

WORKDIR /app

COPY Frontend/package*.json ./

RUN npm install

COPY Frontend .

EXPOSE 3000