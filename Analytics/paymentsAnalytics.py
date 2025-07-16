from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from CustomersApp.models import MonthlyPaymentModel
from django.utils import timezone
from django.db.models import Sum
import calendar
from rest_framework.response import Response
import logging
import ipdb

analytics_logger = logging.getLogger('Analytics')


class PaymentAnalyticsView(APIView):
    '''
        
    '''
    permission_classes = [IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.json_response = {'message': self.message}
        self.request = request
        self.now = timezone.now()
        self.year = self.now.year
        self.bar_chart_data = []
        self.api_response = {
                            "bar_chart_data": [], 
                            "metadata": {
                                "year": self.year,
                                "link_to": ''
                            }
                        }
        return super().dispatch(request, *args, **kwargs)

    def validate_and_parse_input(self):
        self.analytics_type = self.request.data.get('analytics_type')

        if not self.analytics_type or self.analytics_type not in ['monthly_data']:
            analytics_logger.error('Either Analytics type is not coming or wrong type coming from frontend')
            self.status = 400
            self.message = "Something went wrong"

    def build_api_response(self):
        if self.analytics_type == 'monthly_data':
            result = dict(MonthlyPaymentModel.objects
                      .filter(month__year=self.year)
                      .values_list('month__month')
                      .annotate(total_amount=Sum('amount_paid'))
                    )

            for mon in range(1, 13):
                month_total = 0
                if mon in result:
                    month_total = result[mon]

                self.bar_chart_data.append({"x": calendar.month_abbr[mon], "y": month_total})

    def post(self, *args, **kwargs):
        try:
            self.validate_and_parse_input()

            if self.status == 200:
                self.build_api_response()
                self.api_response["bar_chart_data"] = self.bar_chart_data

        except Exception as err:
            analytics_logger.info(err.args[0] if err.args else 'Soomething gone wrong')
            self.message = 'Internal server error'
            self.status = 500

        self.api_response['message'] = self.message
        return Response(self.api_response, status=self.status)
