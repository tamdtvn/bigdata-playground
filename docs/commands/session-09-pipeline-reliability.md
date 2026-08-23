# Validate Compose configuration
docker compose config

# Start/recreate PostgreSQL
docker compose up -d --force-recreate postgres

# Check health status
docker compose ps

# Bring the whole system up and rebuild
docker compose up --build

# Run ingestion as a one-off job
docker compose run --rm ingestion

# Rebuild and run the ingestion job
docker compose run --rm --build ingestion

# Inspect PostgreSQL logs
docker compose logs postgres

# Inspect ingestion logs
docker compose logs ingestion

docker compose up
→ Bring the SYSTEM up.

docker compose run --rm ingestion
→ Run the JOB once.