from django.contrib import admin
from .models import Transaction, RecurringTransaction, TransactionReminder


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'account', 'category', 'transaction_type', 'amount', 'date')
    list_filter = ('transaction_type', 'date', 'category', 'account', 'created_at')
    search_fields = ('description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'account', 'category', 'amount', 'frequency', 'next_due_date', 'is_active')
    list_filter = ('frequency', 'transaction_type', 'is_active', 'created_at')
    search_fields = ('description', 'user__username')
    readonly_fields = ('created_at',)


@admin.register(TransactionReminder)
class TransactionReminderAdmin(admin.ModelAdmin):
    list_display = ('recurring_transaction', 'reminder_date', 'is_sent', 'created_at')
    list_filter = ('is_sent', 'reminder_date', 'created_at')
    readonly_fields = ('created_at',)
