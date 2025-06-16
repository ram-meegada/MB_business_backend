{
    "celery_worker": "celery -A mb_backend worker --loglevel=info",
    "celery_beat": "celery -A mb_backend beat --loglevel=info"
}