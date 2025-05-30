from django.shortcuts import render
from rest_framework.views import APIView
from utils.customPermissions import IsDeliveryAgent, IsDeliveryAgentOrAdmin
from CustomersApp.models import *
from CustomersApp.serializer import *
from rest_framework.response import Response
import logging
from django.db.utils import IntegrityError
from django.db import transaction


customers_logger = logging.getLogger("Customers")

####################### Customer ##############################

class CustomersListView(APIView):
    '''
        This view returns all the active customers
    '''
    permission_classes = [IsDeliveryAgentOrAdmin]
    def get(self, request):
        try:
            customers_list = (CustomerSubscriptionModel.objects
                              .filter(is_active=True)
                              .select_related('user', 'subscription', 'delivery_agent', 'subscription__product', 'subscription__animal'))
            serializer = CustomersListSerializer(customers_list, many=True)
            return Response({"data": serializer.data, "message": "All customer details"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)


class DeliveryAgentsDropDownView(APIView):
    '''
        This view returns all the delivery agents for frontend dropdown
    '''
    permission_classes = [IsDeliveryAgentOrAdmin]
    def get(self, request):
        data = []
        try:
            active_delivery_agents = UserModel.objects.filter(role=3, is_active=True)

            for adg in active_delivery_agents:
                data.append({"id": adg.id, "label": adg.username, "value": adg.username})

            return Response({"data": data, "message": "All Delivery agents"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)
        

class CheckUsernameUniquenessView(APIView):
    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response({"data": None, "message": "Username is required"}, status=400)
        
        username_exists = UserModel.objects.filter(username=username).exists()

        if username_exists:
            return Response({"data": None, "message": "Username not available"}, status=400)
        else:
            return Response({"data": None, "message": "Username is available"}, status=200)
        

class AddCustomerView(APIView):
    permission_classes = [IsDeliveryAgentOrAdmin]
    def post(self, request):
        with transaction.atomic():
            user = UserModel.objects.create(username=request.data["username"], name=request.data["username"], role=2)
            request.data["user"] = user.pk

            serializer = CustomersWriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"data": None, "message": "Customer added successfully"}, status=200)


############## Subscription ###################

class SubscriptionListForDropDownView(APIView):
    '''
        This view returns all the active subscriptions for frontend dropdown
    '''
    def get(self, request):
        data = []
        try:
            subscriptions = SubscriptionPlanModel.objects.filter(is_active=True)

            for subs in subscriptions:
                data.append({"id": subs.id, "label": str(subs), "value": str(subs)})

            return Response({"data": data, "message": "All Subscriptions"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)
