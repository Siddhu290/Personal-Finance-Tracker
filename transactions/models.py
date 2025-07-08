from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Account, Category


class Transaction(models.Model):
    """Individual income/expense transactions"""
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.CharField(max_length=200)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Transfer specific fields
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='received_transfers',
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.transaction_type.title()}: {self.description} - {self.amount}"

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
        
        if self.transaction_type == 'expense':
            return f"-{symbol}{self.amount:,.2f}"
        else:
            return f"+{symbol}{self.amount:,.2f}"


class RecurringTransaction(models.Model):
    """Template for recurring transactions"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_transactions')
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=Transaction.TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.CharField(max_length=200)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    next_due_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['next_due_date']

    def __str__(self):
        return f"{self.description} - {self.frequency}"


class TransactionReminder(models.Model):
    """Reminders for upcoming bills or recurring transactions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    recurring_transaction = models.ForeignKey(
        RecurringTransaction, 
        on_delete=models.CASCADE, 
        related_name='reminders'
    )
    reminder_date = models.DateField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['reminder_date']

    def __str__(self):
        return f"Reminder: {self.recurring_transaction.description} on {self.reminder_date}"
