# Start Postgres

docker run --name mypostgres -e POSTGRES_PASSWORD=postgres_cric -p 5432:5432 -d postgres


# Start pg admin
docker run --name mypgadmin -p 5050:80 -e 'PGADMIN_DEFAULT_EMAIL=your_email@.com' -e 'PGADMIN_DEFAULT_PASSWORD=postgres_cric' -d dpage/pgadmin4
