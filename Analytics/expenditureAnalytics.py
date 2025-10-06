from Expenditure.models import ExpenditureModel
from rest_framework.views import APIView
from utils.expenditureUtils import MONTH_NAMES, PIE_CHART_COLORS, MONTHS_WITH_INT_MAPPING
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
import calendar
from django.db.models import CharField, FloatField, Sum
from django.db.models.functions import Cast
from rest_framework.response import Response


class ExpenditureAnalyticsView(APIView):
    permission_classes = [IsAdminUser]
    '''
        Gives month/yearly wise expenditure
        Analytics Types:- monthly_data, main_categories_analysis, sub_categories_analysis
    '''
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.now = timezone.localtime(timezone.now())
        self.year = self.now.year
        return super().dispatch(request, *args, **kwargs)

    def payload_scrutiny(self):
        if self.request.data.get("year"):
            self.year = self.request.data.get("year")
        self.month = self.request.data.get("month")
        self.category = self.request.data.get("category")

    def post(self, request):
        self.payload_scrutiny()
        graph_data = []

        if self.request.data["analytics_type"] == "monthly_data":
            graph_data = {
                            "bar_chart_data": [],
                            "metadata": {
                                "year": self.year,
                                "link_to": 'main_categories_analysis'
                            }
                        }
            monthly_analytics = dict(ExpenditureModel.objects
                                 .filter(created_at__year=self.year)
                                 .values('created_at__month')
                                 .annotate(month_total=Cast(Sum('amount'), output_field=FloatField()))
                                 .values_list('created_at__month', 'month_total')
                                )

            for mon in range(1, 13):
                month_total = 0
                if mon in monthly_analytics:
                    month_total = monthly_analytics[mon]
                graph_data["bar_chart_data"].append({"x": calendar.month_abbr[mon], "y": month_total})

        elif self.request.data["analytics_type"] == "main_categories_analysis":
            graph_data = {
                            "bar_chart_data": [], 
                            "metadata": {
                                "year": self.year,
                                "month": self.month,
                                "link_to": 'sub_categories_analysis'
                            }
                        }
            if self.month is None:
                return Response({"data": None, "message": "month is required for Main categories analysis"}, status=400)

            exp = dict(ExpenditureModel.objects
                .filter(
                    created_at__month=MONTHS_WITH_INT_MAPPING[self.month],
                    created_at__year=self.year
                )
                .values('category__parent')
                .annotate(am=Cast(Sum('amount'), output_field=FloatField()))
                .values_list('category__parent__name', 'am')
                )

            colors = PIE_CHART_COLORS

            for index, (key, value) in enumerate(exp.items()):
                graph_data["bar_chart_data"].append({ "x": key, "y": value, "color": colors[index] })

        elif self.request.data["analytics_type"] == "sub_categories_analysis":

            if self.month is None:
                return Response({"data": None, "message": "Month is required for Main categories analysis"}, status=400)

            if self.category is None:
                return Response({"data": None, "message": "Category is required for Sub categories analysis"}, status=400)

            graph_data = {
                            "bar_chart_data": [], 
                            "metadata": {
                                "year": self.year,
                                "month": self.month,
                                "category": self.category
                            }
                        }

            exp = dict(ExpenditureModel.objects
                .filter(
                    created_at__year=self.year,
                    created_at__month=MONTHS_WITH_INT_MAPPING[self.month],
                    category__parent__name=self.request.data["category"]
                )
                .values('category')
                .annotate(am=Cast(Sum('amount'), output_field=FloatField()))
                .values_list('category__name', 'am')
                )

            colors = PIE_CHART_COLORS

            for index, (key, value) in enumerate(exp.items()):
                graph_data["bar_chart_data"].append({ "x": key, "y": value, "color": colors[(index + 1)*-1] })

        return Response({"data": graph_data, "message": "Expenditure analytics fetched successfully"}, status=200)
