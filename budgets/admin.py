from django.contrib import admin
from .models import Budget, BudgetAlert


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('category', 'user', 'amount', 'month', 'year', 'get_spent_amount', 'get_utilization_percentage', 'is_active')
    list_filter = ('year', 'month', 'category__category_type', 'is_active', 'created_at')
    search_fields = ('category__name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')

    def get_spent_amount(self, obj):
        return f"${obj.get_spent_amount():,.2f}"
    get_spent_amount.short_description = 'Spent'

    def get_utilization_percentage(self, obj):
        return f"{obj.get_utilization_percentage():.1f}%"
    get_utilization_percentage.short_description = 'Utilization'


@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = ('budget', 'alert_type', 'is_read', 'created_at')
    list_filter = ('alert_type', 'is_read', 'created_at')
    search_fields = ('budget__category__name', 'user__username')
    readonly_fields = ('created_at',)
