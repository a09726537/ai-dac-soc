FROM docker.io/node:22-bookworm AS build



WORKDIR /app



COPY package*.json ./

RUN npm install



COPY . .

RUN npm run build



FROM docker.io/nginx:stable-bookworm



COPY --from=build /app/dist /usr/share/nginx/html



EXPOSE 80



CMD ["nginx", "-g", "daemon off;"]
