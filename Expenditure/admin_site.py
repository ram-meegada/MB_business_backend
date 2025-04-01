from django.contrib import admin
from django.urls import reverse


def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = sorted(app_dict.values(), key=lambda x: x["name"].lower())

    for app in app_list:
        if app["app_label"] == "Expenditure":
            for model in app["models"]:
                if model["object_name"] == "ExpenditureModel":
                    model["add_url"] = reverse("admin:import_politician_data")
    return app_list

# Override the method globally
admin.AdminSite.get_app_list = get_app_list
