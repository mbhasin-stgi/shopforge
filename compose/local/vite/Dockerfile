FROM node:22-alpine AS vite-dev

WORKDIR /app

# Copy the startup script
COPY ./compose/local/vite/npm-start.sh /npm-start.sh
RUN sed -i 's/\r$//g' /npm-start.sh && chmod +x /npm-start.sh

ENTRYPOINT ["/npm-start.sh"]
