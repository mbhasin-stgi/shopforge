FROM postgres:17

# pg_stat_statements ships with the official postgres:17 image.

# Custom initialization script (creates multiple databases if needed)
COPY ./compose/local/postgres/create-multiple-databases.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/create-multiple-databases.sh
