FROM postgres:17

# Install useful extensions
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    postgresql-17-pg-stat-statements \
    && rm -rf /var/lib/apt/lists/*

# Custom initialization script (creates multiple databases if needed)
COPY ./compose/local/postgres/create-multiple-databases.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/create-multiple-databases.sh