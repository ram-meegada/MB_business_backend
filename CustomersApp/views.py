from django.shortcuts import render
from rest_framework.views import APIView
from utils.customPermissions import IsDeliveryAgent, IsDeliveryAgentOrAdmin
from CustomersApp.models import *
from CustomersApp.serializer import *
from rest_framework.response import Response
import logging
from django.db.utils import IntegrityError
from django.db import transaction
from utils.commonUtils import fetch_serializer_error
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Prefetch, Count, Q
from rest_framework.permissions import AllowAny


customers_logger = logging.getLogger("Customers")

####################### Customers (Admin side) ##############################

class CustomersListView(APIView):
    '''
        This view returns all the active customers
    '''
    permission_classes = [IsDeliveryAgentOrAdmin]
    # permission_classes = [AllowAny]
    SERIALIZER_CLASS = CustomersListSerializer

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = (CustomerSubscriptionModel.objects
                              .annotate(
                                  total_turnover=Sum('monthly_payments__amount_paid'), 
                                  payments_pending_count=Count('monthly_payments', filter=Q(monthly_payments__is_paid=False))
                                )
                              .prefetch_related(
                                  Prefetch('monthly_payments', 
                                           queryset=MonthlyPaymentModel.objects.pending_payments().order_by('month'),
                                           to_attr='pending_payments')
                                )
                              .select_related('user', 'subscription', 'delivery_agent', 'subscription__product', 'subscription__animal')
                              .order_by('-created_at'))

    def get(self, request):
        try:
            self.get_queryset()
            serializer = self.SERIALIZER_CLASS(self.queryset, many=True)
            return Response({"data": serializer.data, "message": "All customer details"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)


class CustomersListViewWeb(CustomersListView):
    SERIALIZER_CLASS = CustomersListSerializerForWeb

    def get_queryset(self):
        self.queryset = (CustomerSubscriptionModel.objects
                              .annotate(
                                  total_turnover=Sum('monthly_payments__amount_paid'), 
                                  payments_pending_count=Count('monthly_payments', filter=Q(monthly_payments__is_paid=False))
                                )
                              .select_related('user', 'subscription', 'delivery_agent', 'subscription__product', 'subscription__animal')
                              .order_by('-created_at'))


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
                data.append({"id": adg.pk, "label": adg.username, "value": adg.username})

            return Response({"data": data, "message": "All Delivery agents"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)


class CheckUsernameUniquenessView(APIView):
    permission_classes = [IsDeliveryAgentOrAdmin]
    def post(self, request):
        username = request.data.get("username")

        if not username:
            return Response({"data": None, "message": "Username is required"}, status=400)
        
        username_exists = UserModel.objects.filter(username=username).exists()

        if username_exists:
            return Response({"data": None, "message": "Username not available"}, status=400)
        else:
            return Response({"data": None, "message": "Username is available"}, status=200)


class CustomerByIdView(APIView):
    permission_classes = [IsDeliveryAgentOrAdmin]
    def get(self, request, id):
        customer = (CustomerSubscriptionModel.objects
                              .filter(user_id=id)
                              .annotate(total_turnover=Sum('monthly_payments__amount_paid'))
                              .prefetch_related(
                                  Prefetch('monthly_payments', 
                                           queryset=MonthlyPaymentModel.objects.pending_payments().order_by('month'),
                                           to_attr='pending_payments')
                                )
                              .select_related('user', 'subscription', 'delivery_agent', 'subscription__product', 'subscription__animal')
                              ).first()
        
        if not customer:
            return Response({"data": None, "message": "Customer not found"}, status=400)

        serializer = CustomerDetailsByIdSerializer(customer)
        return Response({"data": serializer.data, "message": "Customer details fetched successfully"}, status=200)


class AddCustomerView(APIView):
    permission_classes = [IsDeliveryAgentOrAdmin]
    def post(self, request):

        if UserModel.objects.filter(username=request.data["username"]).exists():
            return Response({"data": None, "message": "Username already taken"}, status=400)

        user = UserModel.objects.create(username=request.data["username"], name=request.data["name"], role=2)
        request.data["user"] = user.pk

        serializer = CustomersWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        else:
            error = fetch_serializer_error(serializer.errors)
            return Response({"data": None, "message": error}, status=400)
        return Response({"data": None, "message": "Customer added successfully"}, status=200)


########################### Subscription #######################

class SubscriptionListForDropDownView(APIView):
    '''
        This view returns all the active subscriptions for frontend dropdown
    '''
    def get(self, request):
        data = []
        headers = ["Morning Only", "Evening Only", "Both morning and evening"]
        try:
            subscriptions = SubscriptionPlanModel.objects.filter(is_active=True).select_related('product', 'animal')

            for index, i in enumerate(headers):
                data.append({"id": 0, "label": i, "value": i, "isHeader": True})
                subs = subscriptions.filter(schedule=index + 1)
                for j in subs:
                    data.append({"id": j.pk, "label": str(j), "value": str(j)})

            return Response({"data": data, "message": "All Subscriptions"}, status=200)
        except Exception as err:
            customers_logger.error(str(err))
            return Response({"data": None, "message": "Something went wrong"}, status=500)


########################## Payments ###########################

class AllPaymentsView(APIView):
    '''
        Lists all payments by month. Default will be last month payments
    '''
    permission_classes = [IsDeliveryAgentOrAdmin]
    def get(self, request):
        now = timezone.now()
        one_month_back = now - relativedelta(months=1)

        year = one_month_back.year
        month = one_month_back.month

        queryset = MonthlyPaymentModel.objects.filter(month__month=month, month__year=year)
        totals = queryset.aggregate(total_due=Sum('amount_due'), total_paid=Sum('amount_paid'))
        payments = queryset.select_related('customer__user').order_by('-amount_due')

        serializer = PaymentsListingSerializer(payments, many=True)

        data = {"data": serializer.data}

        data["total_due"] = totals["total_due"]
        data["total_paid"] = totals["total_paid"]
        data["total_payment"] = (totals.get("total_due") or 0) + (totals.get("total_paid") or 0)
        data["month"] = datetime.strftime(one_month_back, '%B')
        data["current_year_revenue"] = (MonthlyPaymentModel.objects
                                        .filter(month__year=now.year)
                                        .aggregate(current_year_revenue=Sum('amount_paid'))['current_year_revenue']
                                    )

        return Response({"data": data, "message": "All Payments"}, status=200)


class PaymentByIdView(APIView):
    '''
        Details of payment for particular month.
    '''
    permission_classes = [IsDeliveryAgentOrAdmin]
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.data = {}
        self.message = "Success"
        self.json_response = {'message': self.message}
        self.request = request
        self.payment_id = kwargs['id']
        return super().dispatch(request, *args, **kwargs)

    def prepare_get_request_data(self):
        self.data['name'] = self.payment_obj.customer.user.name
        self.data['month'] = self.payment_obj.payment_month
        self.data['amount_due'] = self.payment_obj.amount_due
        self.data['amount_paid'] = self.payment_obj.amount_paid
        self.data['is_paid'] = self.payment_obj.is_paid
        self.data['payment_date'] = self.payment_obj.payment_date

    def get_payment_object(self):
        self.payment_obj = MonthlyPaymentModel.objects.get(id=self.payment_id)

    def get(self, request, id):
        try:
            self.get_payment_object()
            self.prepare_get_request_data()

            self.json_response['data'] = self.data
        except Exception as err:
            customers_logger.info(err.args[0])
            self.message = 'Something went wrong'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)
    
    def validate_input(self):
        self.amount_due = self.request.data.get('amount_due')
        self.amount_paid = self.request.data.get('amount_paid')
        self.payment_date = self.request.data.get('payment_date')
        self.is_paid = self.request.data.get('is_paid')

    def patch(self, request, id):
        try:
            self.get_payment_object()
            self.validate_input()

            if self.status == 200:
                self.payment_obj.amount_due = self.amount_due
                self.payment_obj.amount_paid = self.amount_paid
                self.payment_obj.payment_date = self.payment_date
                self.payment_obj.is_paid = self.is_paid

                self.payment_obj.save()

        except Exception as err:
            customers_logger.info(err.args[0])
            self.message = 'Something went wrong'
            self.status = 500

        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)


################################# Orders List ###################################

class OrdersListView(APIView):
    permission_classes = [IsDeliveryAgentOrAdmin]
    def dispatch(self, request, *args, **kwargs):
        self.status = 200
        self.message = "Success"
        self.request = request
        self.api_data = None
        self.json_response = {'data': self.api_data, 'message': self.message}
        self.now = timezone.now()
        return super().dispatch(request, *args, **kwargs)

    def make_queryset(self):
        self.orders = OrdersModel.objects.filter(schedule_date=self.date).order_by('-created_at')
        
    def build_api_response(self):
        self.api_data = []

        for order in self.orders:
            temp_dict = {}
            temp_dict['customer'] = {"id": order.customer.user_id, "name": order.customer.user.name}
            temp_dict['subscription'] = str(order.customer.subscription)
            temp_dict['price_at_order'] = order.price_at_order
            temp_dict['is_morning_delivery'] = order.is_morning_delivery
            temp_dict['status'] = order.status

            self.api_data.append(temp_dict)

    def validate_and_parse_input(self):
        self.date = self.request.data.get('date', self.now.date())
    
    def post(self, request):
        try:
            self.validate_and_parse_input()
    
            if self.status == 200:
                self.make_queryset()
                self.build_api_response()
                self.json_response["data"] = self.api_data
    
        except Exception as err:
            customers_logger.info(err.args[0] if err.args else 'Something gone wrong')
            self.message = 'Internal server error'
            self.status = 500
    
        self.json_response['message'] = self.message
        return Response(self.json_response, status=self.status)
