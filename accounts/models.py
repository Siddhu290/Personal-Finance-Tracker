from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, default='USD', choices=[
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('CHF', 'Swiss Franc'),
        ('CNY', 'Chinese Yuan'),
        ('INR', 'Indian Rupee'),
    ])
    dark_mode = models.BooleanField(default=False)
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Account(models.Model):
    """Bank accounts, credit cards, cash, etc."""
    ACCOUNT_TYPES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('investment', 'Investment Account'),
        ('loan', 'Loan Account'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('-999999999.99'))]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"

    def get_balance_display(self):
        """Return formatted balance with currency symbol"""
        currency_symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥',
            'CAD': 'C$', 'AUD': 'A$', 'CHF': 'CHF', 'CNY': '¥', 'INR': '₹'
        }
        symbol = currency_symbols.get(self.user.userprofile.currency, '$')
        return f"{symbol}{self.balance:,.2f}"


class Category(models.Model):
    """Income and expense categories"""
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    icon = models.CharField(max_length=50, default='💰')  # Emoji or icon class
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['category_type', 'name']
        unique_together = ['user', 'name', 'category_type']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
