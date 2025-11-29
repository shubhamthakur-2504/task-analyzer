from django.urls import path
from . import views

urlpatterns = [
    # Main API endpoints
    path('analyze/', views.analyze_tasks, name='analyze_tasks'),
    path('suggest/', views.suggest_tasks, name='suggest_tasks'),
    
    # CRUD operations
    path('', views.task_list_create, name='task_list_create'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('clear/', views.clear_all_tasks, name='clear_all_tasks'),
]