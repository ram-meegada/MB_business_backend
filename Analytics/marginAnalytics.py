from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
import logging
from CustomersApp.models import MonthlyPaymentModel
from Expenditure.models import ExpenditureModel
from django.db.models import Sum
import calendar


analytics_logger = logging.getLogger('Analytics')


class MarginAnalyticsApi(APIView):
    '''
        Profit margin formula:-

        profit = revenue - expenses
        margin = (profit/revenue)*100
    '''
    permission_classes = [IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.request = request
        self.now = timezone.localtime(timezone.now())
        self.year = self.now.year
        self.api_data = {
                            "bar_chart_data": [],
                            "month_exp_and_payment": {},
                            "metadata": {
                                "year": self.year,
                                "link_to": 'fetch_exp_pay_for_month'
                                }
                        }
        self.json_response = {'data': self.api_data, 'message': self.message}
        return super().dispatch(request, *args, **kwargs)
        
    def build_api_response(self):
        expenditure_data = dict(ExpenditureModel.objects
                                 .filter(created_at__year=self.year)
                                 .values('created_at__month')
                                 .annotate(month_total=Sum('amount'))
                                 .values_list('created_at__month', 'month_total')
                                )

        payments_data = dict(MonthlyPaymentModel.objects
                            .filter(month__year=self.year)
                            .values_list('month__month')
                            .annotate(total_amount=Sum('amount_paid'))
                            )
        
        for mon in range(1, 13):
            month_str = calendar.month_abbr[mon]
            total_revenue = payments_data.get(mon, 0)
            total_expenditure = expenditure_data.get(mon, 0)
            margin = 0

            if total_expenditure and total_revenue:
                profit = total_revenue - total_expenditure
                margin = round((profit/total_revenue)*100, 2)

            analytics_logger.info(f'Margin has been calculated successfully:- {margin}')

            self.api_data['bar_chart_data'].append({"x": month_str, "y": margin})
            self.api_data['month_exp_and_payment'][month_str] = {'exp': total_expenditure, 'revenue': total_revenue}

    def validate_and_parse_input(self):
        self.analytics_type = self.request.data.get('analytics_type')

        if not self.analytics_type or self.analytics_type not in ['monthly_data']:
            analytics_logger.error('Either Analytics type is not coming or wrong type coming from frontend')
            self.status = 400
            self.message = "Something went wrong"

    def post(self, request):
        try:
            self.validate_and_parse_input()
    
            if self.status == 200:
                self.build_api_response()
                self.json_response["data"] = self.api_data
    
        except Exception as err:
            analytics_logger.info(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500
    
        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)
