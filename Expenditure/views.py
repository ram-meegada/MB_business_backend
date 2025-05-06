from django.shortcuts import render
from Expenditure.models import ExpenditureModel
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.messages import *
from .serializer import *
from utils.commonUtils import fetch_serializer_error
from django.utils import timezone
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum, Func, F, FloatField
from django.db.models.functions import Cast
from django.db import connection
import json
from utils.expenditureUtils import MONTH_NAMES, PIE_CHART_COLORS, MONTHS_WITH_INT_MAPPING
from rest_framework.permissions import IsAdminUser
from django.http import JsonResponse
from rest_framework.permissions import AllowAny


class ExpenditureView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        serializer = ExpenditureWriteSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": None, "message": "Expenditure added successfully"}, status=201)
        error = fetch_serializer_error(serializer.errors)
        return Response({"data": serializer.errors, "message": error}, status=400)

    def get(self, request):
        all_expenditures = ExpenditureModel.objects.filter(user=request.user).select_related('category', 'category__parent')
        serializer = ExpenditureReadSerializer(all_expenditures, many=True)
        return Response({"data": serializer.data, "message": "All Expenditures fetched successfully"}, status=200)


class ManageExpenditureView(APIView):
    permission_classes = [IsAdminUser]
    def dispatch(self, request, *args, **kwargs):
        id = kwargs["id"]
        self.get_record(id)

        self.request = request
        return super().dispatch(request, *args, **kwargs)

    def get_record(self, id):
        self.exp_record = ExpenditureModel.objects.filter(id=id).first()

    def get(self, *args, **kwargs):
        if not self.exp_record:
            return Response({"data": None, "message": NOT_FOUND}, status=400)
        serializer = ExpenditureReadSerializer(self.exp_record)
        return Response({"data": serializer.data, "message": "Expenditure details fetched successfully"}, status=200)

    def put(self, *args, **kwargs):
        if not self.exp_record:
            return Response({"data": None, "message": NOT_FOUND}, status=400)
        serializer = ExpenditureWriteSerializer(self.exp_record, data=self.request.data, context={"request": self.request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": None, "message": "Expenditure details updated successfully"}, status=200)
        error = fetch_serializer_error(serializer.errors)
        return Response({"data": None, "message": error}, status=400)

    def delete(self, *args, **kwargs):
        if not self.exp_record:
            return Response({"data": None, "message": NOT_FOUND}, status=400)
        self.exp_record.delete()
        return Response({"data": None, "message": "Expenditure details deleted successfully"}, status=200)


class ExpenditureAnalyticsView(APIView):
    permission_classes = [IsAdminUser]
    '''
        Gives month wise expenditure
    '''
    def dispatch(self, request, *args, **kwargs):
        self.request = request
        self.now = timezone.now()
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
                            }
                        }
            monthly_analytics = dict(ExpenditureModel.objects
                                 .filter(user=self.request.user, created_at__year=self.year)
                                 .values('created_at__month')
                                 .annotate(month=Func(
                                     F('created_at__date'), 
                                     function="TO_CHAR", template="TO_CHAR(%(expressions)s, 'Mon')"),
                                     month_total=Cast(Sum('amount'), output_field=FloatField()))
                                 .values_list('month', 'month_total')
                                )
 
            for mon in MONTH_NAMES:
                month_total = 0
                if mon in monthly_analytics:
                    month_total = monthly_analytics[mon]
                graph_data["bar_chart_data"].append({"x": mon, "y": month_total})

        elif self.request.data["analytics_type"] == "main_categories_analysis":
            graph_data = {
                            "pie_chart_data": [], 
                            "metadata": {
                                "year": self.year,
                                "month": self.month
                            }
                        }
            if self.month is None:
                return Response({"data": None, "message": "month is required for Main categories analysis"}, status=400)

            exp = dict(ExpenditureModel.objects
                .filter(
                    user=self.request.user, 
                    created_at__month=MONTHS_WITH_INT_MAPPING[self.month],
                    created_at__year=self.year
                )
                .values('category__parent')
                .annotate(am=Cast(Sum('amount'), output_field=FloatField()))
                .values_list('category__parent__name', 'am')
                )

            colors = PIE_CHART_COLORS

            for index, (key, value) in enumerate(exp.items()):
                graph_data["pie_chart_data"].append({ "x": key, "y": value, "color": colors[index] })

        elif self.request.data["analytics_type"] == "sub_categories_analysis":

            if self.month is None:
                return Response({"data": None, "message": "Month is required for Main categories analysis"}, status=400)

            if self.category is None:
                return Response({"data": None, "message": "Category is required for Sub categories analysis"}, status=400)

            graph_data = {
                            "pie_chart_data": [], 
                            "metadata": {
                                "year": self.year,
                                "month": self.month,
                                "category": self.category
                            }
                        }

            exp = dict(ExpenditureModel.objects
                .filter(
                    user=self.request.user,
                    created_at__year=self.year,
                    created_at__month=timezone.now().month, 
                    category__parent__name=self.request.data["category"]
                )
                .values('category')
                .annotate(am=Cast(Sum('amount'), output_field=FloatField()))
                .values_list('category__name', 'am')
                )

            colors = PIE_CHART_COLORS

            for index, (key, value) in enumerate(exp.items()):
                graph_data["pie_chart_data"].append({ "x": key, "y": value, "color": colors[(index + 1)*-1] })

        return Response({"data": graph_data, "message": "Expenditure analytics fetched successfully"}, status=200)


######################################## Expenditure Category ###########################################

class ExpenditureCategoryView(APIView):
    permission_classes = [IsAdminUser]
    '''
        This API is for adding category and also fetching all categories.
    '''
    def post(self, request):
        serializer = ExpenditureCategorySerilaizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": None, "message": "Expenditure category added successfully"}, status=200)
        error = fetch_serializer_error(serializer.errors)
        return Response({"data": None, "message": error}, status=400)

    def get(self, request):
        '''
            Get API for frontend drop down
        '''
        try:
            data = []
            exp = ExpenditureCategoryModel.objects.filter(parent=None).prefetch_related('subcategories')

            for i in exp:
                data.append({"id": i.id, "label": i.name, "value": i.name, "isHeader": True})
                for j in i.subcategories.all():
                    data.append({"id": j.id, "label": j.name, 'value': j.name})

            return Response({"data": data, "message": "Expenditure categories fetched successfully"}, status=200)
        except Exception as err:
            return Response({"data": None, "message": str(err)}, status=500)
