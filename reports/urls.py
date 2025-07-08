from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Main reports page
    path('', views.ReportsDashboardView.as_view(), name='dashboard'),
    
    # Income vs Expenses
    path('income-expenses/', views.IncomeExpenseReportView.as_view(), name='income_expenses'),
    path('income-expense/', views.IncomeExpenseReportView.as_view(), name='income_expense'),
    
    # Category analysis
    path('category-analysis/', views.CategoryAnalysisView.as_view(), name='category_analysis'),
    
    # Trends and charts
    path('trends/', views.TrendsReportView.as_view(), name='trends'),
    
    # Monthly/Yearly summaries
    path('monthly/', views.MonthlyReportView.as_view(), name='monthly'),
    path('monthly/<int:year>/<int:month>/', views.MonthlyReportView.as_view(), name='monthly_report'),
    path('yearly/', views.YearlyReportView.as_view(), name='yearly'),
    path('yearly/<int:year>/', views.YearlyReportView.as_view(), name='yearly_report'),
    
    # Account summaries
    path('accounts/', views.AccountSummaryView.as_view(), name='account_summary'),
    
    # API endpoints for charts
    path('api/income-expense-chart/', views.get_income_expense_chart_data, name='api_income_expense_chart'),
    path('api/category-pie-chart/', views.get_category_pie_chart_data, name='api_category_pie_chart'),
    path('api/trends-chart/', views.get_trends_chart_data, name='api_trends_chart'),
    path('api/account-balance-chart/', views.get_account_balance_chart_data, name='api_account_balance_chart'),
]
