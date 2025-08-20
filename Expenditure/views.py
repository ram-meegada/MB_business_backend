from django.shortcuts import render
from Expenditure.models import ExpenditureModel
from rest_framework.views import APIView
from rest_framework.response import Response
from utils.messages import *
from .serializer import *
from utils.commonUtils import fetch_serializer_error
from django.utils import timezone
from django.db.models import Q, Sum, Func, F, FloatField
import json
from rest_framework.permissions import IsAdminUser


class ExpenditureView(APIView):
    permission_classes = [IsAdminUser]
    read_serializer = ExpenditureReadSerializer

    def dispatch(self, request, *args, **kwargs):
        self.now = timezone.now()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        serializer = ExpenditureWriteSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"data": None, "message": "Expenditure added successfully"}, status=201)
        error = fetch_serializer_error(serializer.errors)
        return Response({"data": serializer.errors, "message": error}, status=400)

    def get(self, request):
        input_month = request.data.get('month', self.now.date().month)
        all_expenditures = ExpenditureModel.objects.filter(user=request.user, created_at__month=input_month).select_related('category', 'category__parent')
        serializer = self.read_serializer(all_expenditures, many=True)

        current_year_start_date = self.now.replace(month=1, hour=0, minute=0, second=0, microsecond=0)

        data = {}
        data["data"] = serializer.data
        data["current_year_expenditure"] = (ExpenditureModel.objects
                                            .filter(created_at__gte=current_year_start_date)
                                            .aggregate(current_year_expenditure=Sum('amount'))['current_year_expenditure']
                                        )

        return Response({"data": data, "message": "All Expenditures fetched successfully"}, status=200)


class ExpenditureWebView(ExpenditureView):
    read_serializer = ExpenditureReadWebSerializer


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
