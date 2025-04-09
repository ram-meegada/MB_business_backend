from django.core.mail import send_mail
import logging
from django.utils import timezone
from datetime import timedelta, datetime


logger = logging.getLogger("Common")


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
