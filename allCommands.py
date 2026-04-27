{
    "celery_worker": "celery -A mb_backend worker --loglevel=info",
    "celery_beat": "celery -A mb_backend beat --loglevel=info",
    "psql_postgres_connect": "psql -h <rds endpoint> -U postgres -d postgres -p 5432",
    "size_of_db": "SELECT pg_size_pretty(pg_database_size(<DB_NAME>));",

    # DB backup command
    "sql_dump": "pg_dump -h localhost -U your_pg_user -F c -f /tmp/backup.sql your_database_name",

    # DB restore commands
    "drop_database": "PGPASSWORD='Ramu@123' dropdb -h localhost -p 5432 -U postgres MB_Backend",
    "create_database": "PGPASSWORD='Ramu@123' createdb -h localhost -p 5432 -U postgres MB_Backend",
    "restore_database": "PGPASSWORD='Ramu@123' pg_restore -h localhost -U postgres -d MB_Backend --no-owner /tmp/backup.sql"
}