{
    "celery_worker": "celery -A mb_backend worker --loglevel=info",
    "celery_beat": "celery -A mb_backend beat --loglevel=info",
    "psql_postgres_connect": "psql -h <rds endpoint> -U postgres -d postgres -p 5432",
    "size_of_db": "SELECT pg_size_pretty(pg_database_size(<DB_NAME>));",

    # DB backup command
    "sql_dump": "pg_dump -h localhost -U your_pg_user -F c -f /tmp/backup.sql your_database_name",

    # DB restore commands
    "drop_database": "PGPASSWORD='<PASSWORD>' dropdb -h localhost -p <PORT> -U <USER> <DB_NAME>",
    "create_database": "PGPASSWORD='<PASSWORD>' createdb -h localhost -p <PORT> -U <USER> <DB_NAME>",
    "restore_database": "PGPASSWORD='<PASSWORD>' pg_restore -h localhost -U <USER> -d <DB_NAME> --no-owner <BACKUP_FILE_PATH>"
}