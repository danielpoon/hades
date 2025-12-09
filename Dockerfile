FROM postgres:18

# Add initialization scripts if needed:
# COPY docker-entrypoint-initdb.d/ /docker-entrypoint-initdb.d/

EXPOSE 5432

