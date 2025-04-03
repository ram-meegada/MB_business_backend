from django.shortcuts import render
from Expenditure.models import ExpenditureModel
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.messages import *
from .serializer import *
from utils.commonUtils import fetch_serializer_error
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum
from Expenditure.models import ExpenditureCategoryModel


class ExpenditureView(APIView):
    def post(self, request):
        serializer = ExpenditureWriteSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": None, "message": "Expenditure added successfully"}, status=201)
        error = fetch_serializer_error(serializer.errors)
        return Response({"data": serializer.errors, "message": error}, status=400)

    def get(self, request):
        all_expenditures = ExpenditureModel.objects.all()
        serializer = ExpenditureReadSerializer(all_expenditures, many=True)
        return Response({"data": serializer.data, "message": "All Expenditures fetched successfully"}, status=200)


class ManageExpenditureView(APIView):
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
        serializer = ExpenditureReadSerializer(self.exp_record, data=self.request.data, context={"request": self.request})
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
    def get(self, request):
        analytics_result = {}
        today = timezone.now()

        temp = {
            "last_30_days": Q(created_at__gte=(today - timedelta(days=30)), created_at__lte=today),
            "last_3_months": Q(created_at__gte=(today - relativedelta(months=3)), created_at__lte=today),
            "last_6_months": Q(created_at__gte=(today - relativedelta(months=6)), created_at__lte=today),
            "last_1_year": Q(created_at__gte=(today - relativedelta(years=1)), created_at__lte=today),
            "last_2_years": Q(created_at__gte=(today - relativedelta(years=2)), created_at__lte=today),
            "last_3_years": Q(created_at__gte=(today - relativedelta(years=3)), created_at__lte=today),
            "last_5_years": Q(created_at__gte=(today - relativedelta(years=5)), created_at__lte=today)
        }
        for span, query in temp.items():
            analytics_result[span] = ExpenditureModel.objects.filter(query).aggregate(t=Sum('amount'))["t"]
        return Response({"data": analytics_result, "message": "Expenditure analytics fetched successfully"}, status=200)


class ExpenditureCategoryView(APIView):
    '''
        This API is for adding category and also fetching all categories.
    '''
    def post(self, request):
        if not request.data.get("name"):
            return Response({"data": None, "message": "Category name is required"}, status=400)

        ExpenditureCategoryModel.objects.create(name=request.data["name"], parent=request.data.get("parent"))
        return Response({"data": None, "message": "Expenditure category added successfully"}, status=200)
    def get(self, request):
        pass
