import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mb_backend.settings")
django.setup()


def main():
    from livestock.models import LiveStockModel
    from utils.liveStockUtils import generate_new_live_stock_id
    l = LiveStockModel.objects.values("live_stock_id")
    print(l)


def check_live_Stock():
    from livestock.models import LiveStockModel
    l = LiveStockModel.objects.filter(is_active=False, is_deleted=True)
    print(l.values("id", "is_active", "is_deleted"))


def make_superuser():
    from authentication.models import UserModel

    u = UserModel.objects.get(username="mb5")


def generate_new_live_stock():
    from utils.liveStockUtils import generate_new_live_stock_id
    from livestock.models import LiveStockModel
    from django.db.models import Q

    # g = generate_new_live_stock_id("Bhadawari")
    # print(g)
    query = Q(live_stock_id__startswith='B')
    last_id = LiveStockModel.objects.filter(query).values("id", "live_stock_id")
    last_id = last_id.order_by("-live_stock_id")
    print(last_id.values_list('live_stock_id', 'id', 'created_at'), '-----')


def run_script_for_live_stock_id():
    from livestock.models import LiveStockModel
    from django.db.models import Value, F, CharField
    from django.db.models.functions import Concat


def exp_an():
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Q, Sum
    from Expenditure.models import ExpenditureModel

    today = timezone.now()
    q = Q(created_at__gte=(today - timedelta(days=30)), created_at__lte=today)
    ex = ExpenditureModel.objects.filter(q).aggregate(t=Sum('amount'))
    print(ex)


def script_for_categories_creation():
    from Expenditure.models import ExpenditureCategoryModel

    CATEGORY_CHOICES = [
    ("feed", "Feed"),
    ("medicine", "Medicine"),
    ("equipment", "Equipment"),
    ("maintenance", "Maintenance"),
    ("labour", "Labour"),
    ("transportation", "Transportation"),
    ("utilities", "Utilities"),
    ("marketing", "Marketing"),
    ("insurance", "Insurance"),
    ("loan_repayment", "Loan Repayment"),
    ("other", "Other"),
    ]

    SUB_CATEGORY_CHOICES = {
        "feed": [
            ("Green Fodder", "Green Fodder"),
            ("Silage", "Silage"),
            ("Dry Grass", "Dry Grass"),
            ("Hay", "Hay"),
            ("Commercial Feed", "Commercial Feed"),
            ("Minerals & Vitamins", "Minerals & Vitamins"),
            ("Feed Transportation", "Feed Transportation"),
        ],
        "medicine": [
            ("Routine Checkups", "Routine Checkups"),
            ("Vaccinations & Deworming", "Vaccinations & Deworming"),
            ("Medicines & Antibiotics", "Medicines & Antibiotics"),
            ("Artificial Insemination (AI) & Breeding", "Artificial Insemination (AI) & Breeding"),
            ("Pregnancy Care", "Pregnancy Care"),
        ],
        "equipment": [
            ("Milking Machines", "Milking Machines"),
            ("Milk Cans & Storage", "Milk Cans & Storage"),
            ("Water Troughs", "Water Troughs"),
            ("Feed Mixers", "Feed Mixers"),
            ("Cooling Systems", "Cooling Systems"),
            ("Farm Tools & Miscellaneous", "Farm Tools & Miscellaneous"),
        ],
        "maintenance": [
            ("Barn Repairs", "Barn Repairs"),
            ("Fencing Maintenance", "Fencing Maintenance"),
            ("Machinery Servicing", "Machinery Servicing"),
            ("Electric & Plumbing Repairs", "Electric & Plumbing Repairs"),
        ],
        "labour": [
            ("Farm Workers Salary", "Farm Workers Salary"),
            ("Veterinary Assistance", "Veterinary Assistance"),
            ("Milking Staff", "Milking Staff"),
            ("Contract Workers", "Contract Workers"),
        ],
        "transportation": [
            ("Milk Transportation", "Milk Transportation"),
            ("Animal Transport", "Animal Transport"),
            ("Farm Equipment Transport", "Farm Equipment Transport"),
        ],
        "utilities": [
            ("Electricity", "Electricity"),
            ("Water Supply", "Water Supply"),
            ("Internet & Communication", "Internet & Communication"),
            ("Waste Management", "Waste Management"),
        ],
        "marketing": [
            ("Advertising", "Advertising"),
            ("Branding & Packaging", "Branding & Packaging"),
            ("Customer Engagement", "Customer Engagement"),
        ],
        "insurance": [
            ("Livestock Insurance", "Livestock Insurance"),
            ("Farm Property Insurance", "Farm Property Insurance"),
            ("Employee Insurance", "Employee Insurance"),
        ],
        "loan_repayment": [  # Corrected to match the key in CATEGORY_CHOICES
            ("Bank Loan", "Bank Loan"),
            ("Private Loan", "Private Loan"),
            ("Equipment Financing", "Equipment Financing"),
        ],
        "other": [
            ("Miscellaneous", "Miscellaneous"),
            ("Government Compliance", "Government Compliance"),
            ("Farm Expansion", "Farm Expansion"),
        ],
    }

    for i in CATEGORY_CHOICES:
        exp = ExpenditureCategoryModel.objects.create(name=i[1])
        for j in SUB_CATEGORY_CHOICES[i[0]]:
            sub_cat = ExpenditureCategoryModel.objects.create(name=j[1], parent=exp)



if __name__ == "__main__":
    pass
