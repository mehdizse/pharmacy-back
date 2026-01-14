from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('monthly/', views.monthly_report, name='monthly-report'),
    path('monthly-summary/', views.monthly_summary, name='monthly-summary'),
    path('sql-example/', views.sql_example, name='sql-example'),
]
