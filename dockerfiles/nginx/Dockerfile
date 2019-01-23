# get alpine images
FROM nginx:alpine

# Nginx will listen on this port
EXPOSE 8080

# replace NGINX Default Config
RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx

# Remove NGINX Configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY app.conf /etc/nginx/conf.d
