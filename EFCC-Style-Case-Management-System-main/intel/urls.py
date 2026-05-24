from django.urls import path
from . import views

urlpatterns = [
    path('sources/', views.source_list, name='source_list'),
    path('sources/new/', views.source_create, name='source_create'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/new/', views.report_create, name='report_create'),
    path('summary/', views.report_summary, name='report_summary'),
    path('summary/pdf/', views.download_report_pdf, name='download_report_pdf'),
]


