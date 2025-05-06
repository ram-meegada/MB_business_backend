from django.shortcuts import render
from rest_framework.views import APIView
from utils.customPermissions import IsDeliveryAgent
from CustomersApp.models import *
from CustomersApp.serializer import *
from rest_framework.response import Response
import logging


customers_logger = logging.getLogger("Customers")


class CustomersListView(APIView):
    permission_classes = [IsDeliveryAgent]
    def get(self, request):
        try:
            customers_list = CustomerSubscriptionModel.objects.all()
            print(customers_list, '-------customers_list-----')
            serializer = CustomersListSerializer(customers_list, many=True)
            return Response({"data": serializer.data, "message": "All customer details"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)
