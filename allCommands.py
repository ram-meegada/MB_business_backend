{
    "celery_worker": "celery -A mb_backend worker --loglevel=info",
    "celery_beat": "celery -A mb_backend beat --loglevel=info",
    "psql_postgres_connect": "psql -h <rds endpoint> -U postgres -d postgres -p 5432"
}