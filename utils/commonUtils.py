from django.db import models
from django.core.mail import send_mail
import logging
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import connection
import tracemalloc


logger = logging.getLogger("Common")


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


def fetch_serializer_error(serializer_errors: dict) -> str:
    data = dict(serializer_errors)
    key = list(data.keys())[0]
    return data[key][0]


def send_simple_mail(subject, message, to_mails):
    try:
        send_mail(subject, message, None, to_mails, fail_silently=False)
    except Exception as err:
        logger.error(f"Mail sending failed with error:- {err}")


def created_at_verbose(created_at):
    try:
        now = timezone.now()

        if created_at >= (now - timedelta(hours=24)):
            seconds = (now - created_at).seconds

            if seconds < 60:
                return f"{seconds} second ago" if seconds == 1 else f"{seconds} seconds ago"
            elif seconds >= 60 and seconds < 3600:
                minutes = seconds//60
                return f"{minutes} minute ago" if minutes == 60 else f"{minutes} minutes ago"
            else:
                hours = seconds//3600
                return f"{hours} hour ago" if hours == 60 else f"{hours} hours ago"

        else:
            return datetime.strftime(created_at, "%d %B %Y")

    except Exception as err:
        logger.error(f"created_at_verbose function failed with error:- {err}")
        return ""


def debugging_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()

        tracemalloc.start()
        mem_snapshot_one = tracemalloc.take_snapshot()

        result = func(*args, **kwargs)

        mem_snapshot_two = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = mem_snapshot_two.compare_to(mem_snapshot_one, 'lineno')
        total_memory_taken = sum([stat.size_diff for stat in stats])

        logger.info(f'Number of queries taken, {len(connection.queries)}')
        logger.info(f'Total Execution time, {datetime.now() - start_time}')
        logger.info(f'Total memory taken, {total_memory_taken/1024} KB')

        return result
    return wrapper
