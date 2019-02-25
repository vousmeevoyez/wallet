# get alpine images
FROM nginx:alpine

# Nginx will listen on this port
EXPOSE 8080

# Remove NGINX Configuration
RUN rm /etc/nginx/conf.d/default.conf
COPY app.conf /etc/nginx/conf.d
