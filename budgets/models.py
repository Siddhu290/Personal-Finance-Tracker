from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Category
from django.db.models import Sum
from datetime import datetime


class Budget(models.Model):
    """Monthly budgets for different categories"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    month = models.IntegerField()  # 1-12
    year = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['-year', '-month', 'category__name']

    def __str__(self):
        return f"{self.category.name} Budget - {self.year}/{self.month:02d}"

    def get_spent_amount(self):
        """Calculate how much has been spent in this budget period"""
        from transactions.models import Transaction
        
        spent = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            date__year=self.year,
            date__month=self.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        return spent

    def get_remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.amount - self.get_spent_amount()

    def get_utilization_percentage(self):
        """Calculate budget utilization as percentage"""
        spent = self.get_spent_amount()
        if self.amount > 0:
            return min(float(spent / self.amount * 100), 100)
        return 0

    def is_over_budget(self):
        """Check if budget is exceeded"""
        return self.get_spent_amount() > self.amount

    def get_amount_display(self):
        """Return formatted amount with currency symbol"""
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'CAD': 'C$', 'AUD': 'A$', 'CHF': 'CHF', 'CNY': '¥', 'INR': '₹'
        }
        try:
            symbol = currency_symbols.get(self.user.userprofile.currency, '$')
        except:
            symbol = '$'
        return f"{symbol}{self.amount:,.2f}"


class BudgetAlert(models.Model):
    """Alerts for budget overspending"""
    ALERT_TYPES = [
        ('warning', 'Warning (80% spent)'),
        ('danger', 'Danger (100% spent)'),
        ('critical', 'Critical (Over budget)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_alerts')
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.alert_type.title()} Alert for {self.budget.category.name}"
