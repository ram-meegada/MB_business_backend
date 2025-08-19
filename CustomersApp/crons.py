from django_cron import CronJobBase, Schedule
from django.utils import timezone
from CustomersApp.models import *
from django.db.models import Q, Sum
from dateutil.relativedelta import relativedelta
from datetime import date
import logging
import ipdb
from django.db.utils import IntegrityError

crons_logger = logging.getLogger('Crons')


class CreateDailyOrdersCron(CronJobBase):
    """
        Cron to create orders for morning and evening
    """
    RUN_AT_TIMES = ['01:00', '13:00']
    RETRY_AFTER_FAILURE_MINS = 1
    MIN_NUM_FAILURES = 1

    schedule = Schedule(run_at_times=RUN_AT_TIMES, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = "CreateOrderCron"

    def do(self):
        now = timezone.localtime(timezone.now())
        today_date = now.date()
        shift = ""

        if now.hour in range(12, 23):
            shift = "evening"
            query = Q(subscription__schedule__in=[2, 3])
        elif now.hour in range(0, 12):
            shift = "morning"
            query = Q(subscription__schedule__in=[1, 3])

        if not shift:
            raise Exception('Something gone wrong.')

        customer_subscriptions = CustomerSubscriptionModel.objects.filter(query, is_active=True)
        already_created_orders = set(OrdersModel.objects.filter(schedule_date=today_date).values_list('customer', 'is_morning_delivery', 'schedule_date'))
        order_objs = []

        for cus_sub in customer_subscriptions:
            is_morning_delivery = False if shift == "evening" else True

            if (cus_sub.pk, is_morning_delivery, today_date) not in already_created_orders:
                ord_obj = OrdersModel(status="pending", 
                                        is_morning_delivery=False if shift == "evening" else True,
                                        customer=cus_sub,
                                        price_at_order=cus_sub.subscription.price if shift == "morning" else cus_sub.subscription.evening_price,
                                        schedule_date=today_date
                                    )
                order_objs.append(ord_obj)
            else:
                crons_logger.info(f'Order for {cus_sub.user.name} on date {today_date} for {shift} is already created.')

        #Create orders as bulk list
        if order_objs:
            OrdersModel.objects.bulk_create(order_objs)
            crons_logger.info(f'{len(order_objs)} order created for {shift}')


class GenerateMonthlyPaymentsCron(CronJobBase):
    '''
        On first day of every month we will generate payments of previous month.
    '''
    RUN_MONTHLY_ON_DAYS = [1]
    RUN_AT_TIMES = ['00:10']
    RETRY_AFTER_FAILURE_MINS = 60 * 60
    MIN_NUM_FAILURES = 1

    schedule = Schedule(run_monthly_on_days=RUN_MONTHLY_ON_DAYS, run_at_times=RUN_AT_TIMES, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = "GenerateMonthlyPaymentsCron"

    def do(self):
        today = timezone.localtime(timezone.now())
        one_month_back = today - relativedelta(months=1)

        year = one_month_back.year
        month = one_month_back.month
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
            crons_logger.info(f'{len(payment_bulklist)} payments created.')
