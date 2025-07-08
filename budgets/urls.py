from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    # Budget management
    path('', views.BudgetListView.as_view(), name='budget_list'),
    path('create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('<int:pk>/edit/', views.BudgetUpdateView.as_view(), name='budget_edit'),
    path('<int:pk>/update/', views.BudgetUpdateView.as_view(), name='budget_update'),
    path('<int:pk>/delete/', views.BudgetDeleteView.as_view(), name='budget_delete'),
    
    # Budget overview and analysis
    path('overview/', views.BudgetOverviewView.as_view(), name='budget_overview'),
    path('analysis/', views.BudgetAnalysisView.as_view(), name='budget_analysis'),
    path('analysis/<int:year>/<int:month>/', views.BudgetAnalysisView.as_view(), name='budget_analysis_detailed'),
    
    # Budget alerts
    path('alerts/', views.BudgetAlertListView.as_view(), name='alert_list'),
    path('alerts/<int:pk>/mark-read/', views.mark_alert_read, name='mark_alert_read'),
    
    # API endpoints
    path('api/budget-data/<int:year>/<int:month>/', views.get_budget_data, name='api_budget_data'),
]
