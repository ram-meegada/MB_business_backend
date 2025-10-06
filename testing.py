import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings.dev")
django.setup()

from django.db import connection, reset_queries
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from django.conf import settings


def main():
    from Expenditure.models import ExpenditureCategoryModel, ExpenditureModel
    from django.db.models import Prefetch
    from django.utils import timezone
    from dateutil.relativedelta import relativedelta
    from datetime import datetime
    from django.db.models import Sum, Q, F, Func, FloatField
    from django.db.models.functions import Cast
    import json
    from django.db import reset_queries, connection

    reset_queries()
    z = []
    res = ExpenditureCategoryModel.objects.filter(parent=None)
    for i in res:
        temp = {"parent": i.name}
        temp["children"] = list(ExpenditureCategoryModel.objects.filter(parent=i).values_list('name', flat=True))
        z.append(temp)
    
    print(z)


def run_crons():
    from CustomersApp.tasks import create_orders_for_the_day, generate_monthly_payments

    # create_orders_for_the_day()
    generate_monthly_payments()


def data_migration_for_june_orders():
    from CustomersApp.models import CustomerSubscriptionModel, OrdersModel
    from datetime import date, timedelta
    from django.db.models import Q
    import ipdb

    today = date.today()
    start_date = today.replace(month=6, day=1)
    order_objs = []

    for _ in range(30):
        for i in range(2):
            if i == 0:
                query = Q(subscription__schedule__in=[1, 3])
            elif i == 1:
                query = Q(subscription__schedule__in=[2, 3])
            
            subscriptions = CustomerSubscriptionModel.objects.filter(query)

            for cus_sub in subscriptions:
                ord_obj = OrdersModel(status="delivered",
                                        is_morning_delivery=True if i == 0 else False, 
                                        customer=cus_sub,
                                        price_at_order=cus_sub.subscription.price if i == 0 else cus_sub.subscription.evening_price,
                                        schedule_date=start_date
                                        )
                order_objs.append(ord_obj)

        start_date += timedelta(days=1)

    if order_objs:
        OrdersModel.objects.bulk_create(order_objs)


def test_gpt_mini():
    from openai import OpenAI

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate Telugu voter data into English fields. Call me boss"},
            {"role": "user", "content": "ఓటరు పేరు: వెంకట రమణ సరిపల్లి"}
        ]
    )

    print(response.choices[0].message.content)


def ingest_gpt_data():
    from langchain.vectorstores import Chroma
    from langchain.embeddings import OpenAIEmbeddings
    from django.conf import settings

    orders = [
        "Order ID 3779: Customer Sakala Moogodu has an evening subscription for 500 ml buffalo milk at ₹40. Delivery status: pending.",
        "Order ID 3765: Customer Jathregamma received morning delivery of 500 ml buffalo milk at ₹40. Delivery status: delivered.",
        "Order ID 3768: Customer Gudivada 4th floor received morning delivery of 1 L buffalo milk and evening 250 ml milk at ₹80 and ₹20 respectively. Status: delivered.",
    ]

    embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
    db = Chroma(persist_directory=settings.PERSIST_DIRECTORY, embedding_function=embeddings)
    # rows = db._collection.get()['ids']

    # if rows:
    #     db._collection.delete(ids=rows)
    #     db.persist()
    # Store all orders in the vector database
    db.add_texts(orders)
    # for i, j in zip(rows['ids'][-10:], rows['documents'][-10:]):
    #     print(i, j)


def query_vector_db():
    query = "what subscription does sakala moogodu has?"
    embeddings = OpenAIEmbeddings()
    VECTOR_DB = Chroma(embedding_function=embeddings, persist_directory=settings.PERSIST_DIRECTORY)

    docs = VECTOR_DB.similarity_search(query, k=2)

    for doc in docs:
        print("🔎", doc.page_content)


if __name__ == "__main__":
    query_vector_db()
    # ingest_gpt_data()
    # test_gpt_mini()
    # test()
    # data_migration_for_june_orders()
    pass
