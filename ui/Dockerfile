FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy static UI files
COPY index.html /usr/share/nginx/html/index.html
COPY config/ /usr/share/nginx/html/config/

EXPOSE 80
