from django.urls import path
from policies.views import *

urlpatterns = [
    path("", policy_list_create_view, name="policies"),
    path("<int:pk>/", policy_detail_view, name="policy_detail"),
    path("<int:pk>/acknowledge/", policy_acknowledge_view,
         name="policy_acknowledge"),
    path("my-acknowledgments/", my_acknowledgments, name="my-acknowledgments"),
    path("pending-acknowledgements/", pending_acknowledgements,
         name="pending_acknowledgements"),
    path("categories/", policy_category_list_create_view, name="policy_category"),

]
