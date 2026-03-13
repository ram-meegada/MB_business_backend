from django.db import connection, reset_queries
import logging
from utils.commonUtils import send_simple_mail
from django.conf import settings
from threading import Thread

common_logger = logging.getLogger("Common")


class QueriesCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        reset_queries()

        self.request = request
        response = self.get_response(request)

        self.count_queries()

        return response

    def count_queries(self):
        if self.request.path.startswith('/admin/'):
            return

        all_queries = connection.queries

        if len(all_queries) > 5 and settings.SEND_MAIL_OVER_QUERIES:
            common_logger.warning(f"Queries Count exceeded:- {len(all_queries)}, Path:- {self.request.path}, sending mail........")
            Thread(
                target=send_simple_mail, 
                args=("Queries Count", f"Queries count exceeded threshold for path:- {self.request.path}\nCount:- {len(all_queries)}", settings.ADMINS)
            ).start()

        common_logger.info(f"Queries Count:- {len(all_queries)}, Path:- {self.request.path}")
