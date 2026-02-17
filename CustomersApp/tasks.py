from CustomersApp.models import OrdersModel, CustomerSubscriptionModel, MonthlyPaymentModel
from celery import shared_task
from utils.commonUtils import send_simple_mail
from django.conf import settings
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def create_orders_for_the_day(self):
    '''
        This task creates orders for morning and evening
    '''
    try:
        now = timezone.localtime(timezone.now())
        exclude_query = Q()
        shift = ""

        if now.hour in range(12, 23):
            shift = "evening"
            query = Q(subscription__schedule__in=[2, 3])
        elif now.hour in range(0, 12):
            shift = "morning"
            query = Q(subscription__schedule__in=[1, 3])
        is_morning_delivery = False if shift == "evening" else True

        customer_subscriptions = CustomerSubscriptionModel.objects.filter(query, is_active=True)
        aleady_created_orders = (OrdersModel.objects
                                 .filter(
                                     schedule_date=now.date(), 
                                     is_morning_delivery=is_morning_delivery).values_list('customer', flat=True)
                                )
        customer_subscriptions = customer_subscriptions.exclude(id__in=aleady_created_orders)
        order_objs = []

        for cus_sub in customer_subscriptions:
            ord_obj = OrdersModel(status="pending", 
                                    is_morning_delivery=is_morning_delivery, 
                                    customer=cus_sub, 
                                    price_at_order=cus_sub.subscription.price if shift == "morning" else cus_sub.subscription.evening_price,
                                    schedule_date=now.today()
                                    )
            order_objs.append(ord_obj)

        #Create orders as bulk list
        if order_objs: OrdersModel.objects.bulk_create(order_objs)
        print(f"{len(order_objs)} orders created for {shift} shift")
    except Exception as err:
        send_simple_mail("Create orders for the day cron failed!", str(err), [settings.PRIMARY_MAIL])
        raise self.retry(exc=err)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def generate_monthly_payments(self):
    try:
        today = timezone.localtime(timezone.now())
        today = today - relativedelta(months=1)

        year = today.year
        month = today.month
        payments_month = date(year, month, 1)

        already_created_cus_payments = MonthlyPaymentModel.objects.filter(month=payments_month).values_list('customer')

        cus_totals = (OrdersModel.objects
                      .filter(schedule_date__month=month, schedule_date__year=year)
                      .exclude(customer__in=already_created_cus_payments)
                      .values('customer')
                      .annotate(total=Sum('price_at_order'))
                    )

        payment_bulklist = []

        for payment in cus_totals:
            payment_bulklist.append(MonthlyPaymentModel(
                customer_id=payment['customer'],
                month=payments_month,
                amount_due=payment['total']
            ))

        if payment_bulklist:
            MonthlyPaymentModel.objects.bulk_create(payment_bulklist)

    except Exception as err:
        send_simple_mail("Generate monthly payments cron failed!", str(err), [settings.PRIMARY_MAIL])
        raise self.retry(exc=err)
