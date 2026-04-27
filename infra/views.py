from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from CustomersApp.models import OrdersModel
import logging
from dateutil import parser as dtparser
from CustomersApp.models import CustomerSubscriptionModel
from datetime import timedelta
import sys
from rest_framework.permissions import IsAdminUser
from linkedIn_jobs.models import Skill, SKILLS_MAPPING

common_logger = logging.getLogger('Common')


class BackfillOrdersView(APIView):
    permission_classes = [IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.request = request
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
        return super().dispatch(request, *args, **kwargs)
        
    def build_api_response(self):
        customer_subscriptions = CustomerSubscriptionModel.objects.all()
        aleady_created_orders = (OrdersModel.objects
                                    .filter(schedule_date__gte=self.start_date, schedule_date__lte=self.end_date)
                                    .values_list('customer', 'schedule_date', 'is_morning_delivery')
                                )

        order_objs = []
        while self.start_date <= self.end_date:
            for cus_sub in customer_subscriptions:
                if (cus_sub.id, self.start_date, True) not in aleady_created_orders and cus_sub.subscription.schedule in [1, 3]:
                    mrng_ord_obj = OrdersModel(status="delivered", is_morning_delivery=True, customer=cus_sub, 
                                          price_at_order=cus_sub.subscription.price, schedule_date=self.start_date)
                    order_objs.append(mrng_ord_obj)
                if (cus_sub.id, self.start_date, False) not in aleady_created_orders and cus_sub.subscription.schedule in [2, 3]:
                    evng_ord_obj = OrdersModel(status="delivered", is_morning_delivery=False, customer=cus_sub,
                                          price_at_order=cus_sub.subscription.evening_price, schedule_date=self.start_date)
                    order_objs.append(evng_ord_obj)
            
            self.start_date += timedelta(days=1)

        #Create orders as bulk list
        if order_objs:
            OrdersModel.objects.bulk_create(order_objs)

        self.api_data = {'message': f'{len(order_objs)} orders backfilled successfully!'}

    def validate_and_parse_input(self):
        start_date = self.request.data['start_date']
        end_date = self.request.data['end_date']

        self.start_date = dtparser.parse(start_date).date()
        self.end_date = dtparser.parse(end_date).date()

    def post(self, request):
        try:
            self.validate_and_parse_input()

            if self.status == 200:
                self.build_api_response()
                self.json_response["data"] = self.api_data

        except Exception as err:
            print(err, '----err----')
            common_logger.info(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)

class GetSysVersionAPI(APIView):    
    permission_classes = [IsAdminUser]
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.request = request
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
        return super().dispatch(request, *args, **kwargs)
        
    def build_api_response(self):
        data = {}

        data['python_version'] = sys.version
        self.api_data = data

    def validate_and_parse_input(self):
        pass

    def get(self, request):
        try:
            self.validate_and_parse_input()

            if self.status == 200:
                self.build_api_response()
                self.json_response["data"] = self.api_data

        except Exception as err:
            common_logger.info(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)

class PushCanonicalSkillsToDB(APIView):
    permission_classes = [IsAdminUser]

    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.request = request
        self.api_data = {}
        self.json_response = {'data': self.api_data, 'message': self.message}
        return super().dispatch(request, *args, **kwargs)
        
    def push_canonical_skills_to_db(self):
        bulk_lst = []

        already_updated_skills = set(Skill.objects.filter(is_approved=True).values_list('name', 'category'))

        for category, skills in SKILLS_MAPPING.items():
            for skill in skills:
                if (skill, category) not in already_updated_skills:
                    bulk_lst.append(Skill(name=skill, category=category, is_approved=True))

        Skill.objects.bulk_create(bulk_lst)
        self.api_data['added_skills_count'] = len(bulk_lst)

    def validate_and_parse_input(self):
        pass

    def post(self, request):
        try:
            self.validate_and_parse_input()

            if self.status == 200:
                self.push_canonical_skills_to_db()
                self.json_response["data"] = self.api_data

        except Exception as err:
            common_logger.exception(err.args[0] if err.args else 'Something gone wrong')
            self.message = str(err)
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)
