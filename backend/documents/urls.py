from django.urls import path
from documents.views import *

urlpatterns = [
    path("", get_all_docs, name="all-docs"),
    path("types/", document_type_list_create_view, name="document_typeslc"),
    path("types/<int:pk>/", document_type_detail_view, name="doc_type_detail"),
    path("templates/", document_template_list_create_view, name="doc_templates"),
    path("templates/<int:pk>/", document_template_detail_view,
         name="doc_template_detail"),
    path('request/', document_request_list_create_view,
         name="document_request_list_create"),

]
