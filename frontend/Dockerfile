FROM node:22-slim

WORKDIR /app

COPY package*.json ./

RUN NODE_OPTIONS=--max-old-space-size=4096 npm install --legacy-peer-deps --prefer-offline

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
