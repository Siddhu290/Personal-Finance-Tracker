from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Transaction management
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/create/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<int:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<int:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),
    
    # Transfer between accounts
    path('transfer/', views.TransferCreateView.as_view(), name='transfer_create'),
    
    # Recurring transactions
    path('recurring/', views.RecurringTransactionListView.as_view(), name='recurring_list'),
    path('recurring/create/', views.RecurringTransactionCreateView.as_view(), name='recurring_create'),
    path('recurring/<int:pk>/edit/', views.RecurringTransactionUpdateView.as_view(), name='recurring_edit'),
    path('recurring/<int:pk>/delete/', views.RecurringTransactionDeleteView.as_view(), name='recurring_delete'),
    path('recurring/<int:pk>/execute/', views.ExecuteRecurringTransactionView.as_view(), name='recurring_execute'),
    
    # Import/Export
    path('import/', views.ImportTransactionsView.as_view(), name='import_transactions'),
    path('export/', views.ExportTransactionsView.as_view(), name='export_transactions'),
    path('download-sample-csv/', views.download_sample_csv, name='download_sample_csv'),
    
    # Search and filter
    path('search/', views.TransactionSearchView.as_view(), name='transaction_search'),
    
    # API endpoints for AJAX
    path('api/account-balance/<int:account_id>/', views.get_account_balance, name='api_account_balance'),
]
