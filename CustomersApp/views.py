from django.shortcuts import render
from rest_framework.views import APIView
from utils.customPermissions import IsDeliveryAgent, IsDeliveryAgentOrAdmin
from CustomersApp.models import *
from CustomersApp.serializer import *
from rest_framework.response import Response
import logging


customers_logger = logging.getLogger("Customers")


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
