#!/usr/bin/env python
"""
Management command to create sample data for the Finance Tracker application.
Run this script to populate the database with demo data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile, Account, Category
from transactions.models import Transaction, RecurringTransaction
from budgets.models import Budget

def create_sample_data():
    """Create sample data for the application."""
    
    print("Creating sample data...")
    
    # Create demo user
    demo_user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Demo',
            'last_name': 'User'
        }
    )
    if created:
        demo_user.set_password('demo123')
        demo_user.save()
        print("✓ Demo user created")
    else:
        print("✓ Demo user already exists")
    
    # Create admin user
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Admin user created")
    else:
        print("✓ Admin user already exists")
    
    # Create admin user profile
    admin_profile, created = UserProfile.objects.get_or_create(
        user=admin_user,
        defaults={
            'dark_mode': False,
            'currency': 'USD',
            'email_notifications': True,
            'budget_alerts': True
        }
    )
    if created:
        print("✓ Admin user profile created")
    
    # Create demo user profile
    profile, created = UserProfile.objects.get_or_create(
        user=demo_user,
        defaults={
            'dark_mode': False,
            'currency': 'USD',
            'email_notifications': True,
            'budget_alerts': True
        }
    )
    if created:
        print("✓ Demo user profile created")
    else:
        print("✓ Demo user profile already exists")
    print("✓ User profile created")
    
    # Create accounts
    accounts_data = [
        {
            'name': 'Primary Checking',
            'account_type': 'checking',
            'balance': Decimal('2500.00'),
        },
        {
            'name': 'Emergency Savings',
            'account_type': 'savings',
            'balance': Decimal('15000.00'),
        },
        {
            'name': 'Credit Card',
            'account_type': 'credit_card',
            'balance': Decimal('-850.00'),
        },
        {
            'name': 'Cash Wallet',
            'account_type': 'cash',
            'balance': Decimal('150.00'),
        },
        {
            'name': 'Investment Account',
            'account_type': 'investment',
            'balance': Decimal('8500.00'),
        }
    ]
    
    accounts = {}
    for account_data in accounts_data:
        account, created = Account.objects.get_or_create(
            user=demo_user,
            name=account_data['name'],
            defaults=account_data
        )
        accounts[account_data['name']] = account
    print("✓ Sample accounts created")
    
    # Create categories
    income_categories_data = [
        {'name': 'Salary', 'category_type': 'income', 'color': '#10B981', 'icon': 'fas fa-briefcase'},
        {'name': 'Freelance', 'category_type': 'income', 'color': '#3B82F6', 'icon': 'fas fa-laptop'},
        {'name': 'Investment Returns', 'category_type': 'income', 'color': '#8B5CF6', 'icon': 'fas fa-chart-line'},
        {'name': 'Side Business', 'category_type': 'income', 'color': '#06B6D4', 'icon': 'fas fa-store'},
        {'name': 'Gifts', 'category_type': 'income', 'color': '#EC4899', 'icon': 'fas fa-gift'},
    ]
    
    expense_categories_data = [
        {'name': 'Groceries', 'category_type': 'expense', 'color': '#EF4444', 'icon': 'fas fa-shopping-cart'},
        {'name': 'Transportation', 'category_type': 'expense', 'color': '#F59E0B', 'icon': 'fas fa-car'},
        {'name': 'Utilities', 'category_type': 'expense', 'color': '#6B7280', 'icon': 'fas fa-bolt'},
        {'name': 'Entertainment', 'category_type': 'expense', 'color': '#EC4899', 'icon': 'fas fa-film'},
        {'name': 'Healthcare', 'category_type': 'expense', 'color': '#14B8A6', 'icon': 'fas fa-heartbeat'},
        {'name': 'Dining Out', 'category_type': 'expense', 'color': '#F97316', 'icon': 'fas fa-utensils'},
        {'name': 'Shopping', 'category_type': 'expense', 'color': '#A855F7', 'icon': 'fas fa-shopping-bag'},
        {'name': 'Insurance', 'category_type': 'expense', 'color': '#64748B', 'icon': 'fas fa-shield-alt'},
        {'name': 'Education', 'category_type': 'expense', 'color': '#0EA5E9', 'icon': 'fas fa-graduation-cap'},
        {'name': 'Home Maintenance', 'category_type': 'expense', 'color': '#84CC16', 'icon': 'fas fa-home'},
    ]
    
    categories = {}
    for cat_data in income_categories_data + expense_categories_data:
        category, created = Category.objects.get_or_create(
            user=demo_user,
            name=cat_data['name'],
            defaults=cat_data
        )
        categories[cat_data['name']] = category
    print("✓ Sample categories created")
    
    # Create sample transactions (last 3 months)
    transactions_data = [
        # Income transactions
        {'description': 'Monthly Salary', 'amount': Decimal('4500.00'), 'type': 'income', 'account': 'Primary Checking', 'category': 'Salary', 'days_ago': 5},
        {'description': 'Freelance Project', 'amount': Decimal('800.00'), 'type': 'income', 'account': 'Primary Checking', 'category': 'Freelance', 'days_ago': 12},
        {'description': 'Previous Month Salary', 'amount': Decimal('4500.00'), 'type': 'income', 'account': 'Primary Checking', 'category': 'Salary', 'days_ago': 35},
        {'description': 'Dividend Payment', 'amount': Decimal('125.00'), 'type': 'income', 'account': 'Investment Account', 'category': 'Investment Returns', 'days_ago': 22},
        
        # Expense transactions
        {'description': 'Grocery Store', 'amount': Decimal('85.50'), 'type': 'expense', 'account': 'Primary Checking', 'category': 'Groceries', 'days_ago': 2},
        {'description': 'Gas Station', 'amount': Decimal('45.00'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Transportation', 'days_ago': 3},
        {'description': 'Electric Bill', 'amount': Decimal('125.00'), 'type': 'expense', 'account': 'Primary Checking', 'category': 'Utilities', 'days_ago': 7},
        {'description': 'Netflix Subscription', 'amount': Decimal('15.99'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Entertainment', 'days_ago': 1},
        {'description': 'Restaurant Dinner', 'amount': Decimal('75.00'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Dining Out', 'days_ago': 4},
        {'description': 'Grocery Store', 'amount': Decimal('120.75'), 'type': 'expense', 'account': 'Primary Checking', 'category': 'Groceries', 'days_ago': 9},
        {'description': 'Coffee Shop', 'amount': Decimal('12.50'), 'type': 'expense', 'account': 'Cash Wallet', 'category': 'Dining Out', 'days_ago': 1},
        {'description': 'Uber Ride', 'amount': Decimal('18.00'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Transportation', 'days_ago': 6},
        {'description': 'Online Shopping', 'amount': Decimal('89.99'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Shopping', 'days_ago': 8},
        {'description': 'Internet Bill', 'amount': Decimal('65.00'), 'type': 'expense', 'account': 'Primary Checking', 'category': 'Utilities', 'days_ago': 15},
        {'description': 'Movie Tickets', 'amount': Decimal('28.00'), 'type': 'expense', 'account': 'Credit Card', 'category': 'Entertainment', 'days_ago': 10},
    ]
    
    for trans_data in transactions_data:
        transaction_date = datetime.now().date() - timedelta(days=trans_data['days_ago'])
        transaction, created = Transaction.objects.get_or_create(
            user=demo_user,
            description=trans_data['description'],
            amount=trans_data['amount'],
            date=transaction_date,
            defaults={
                'transaction_type': trans_data['type'],
                'account': accounts[trans_data['account']],
                'category': categories[trans_data['category']],
            }
        )
    print("✓ Sample transactions created")
    
    # Create recurring transactions
    from dateutil.relativedelta import relativedelta
    
    recurring_data = [
        {
            'description': 'Monthly Salary',
            'amount': Decimal('4500.00'),
            'transaction_type': 'income',
            'account': accounts['Primary Checking'],
            'category': categories['Salary'],
            'frequency': 'monthly',
            'start_date': datetime.now().date().replace(day=1),
            'next_due_date': datetime.now().date().replace(day=1) + relativedelta(months=1),
            'is_active': True
        },
        {
            'description': 'Rent Payment',
            'amount': Decimal('1200.00'),
            'transaction_type': 'expense',
            'account': accounts['Primary Checking'],
            'category': categories['Home Maintenance'],
            'frequency': 'monthly',
            'start_date': datetime.now().date().replace(day=1),
            'next_due_date': datetime.now().date().replace(day=1) + relativedelta(months=1),
            'is_active': True
        },
        {
            'description': 'Netflix Subscription',
            'amount': Decimal('15.99'),
            'transaction_type': 'expense',
            'account': accounts['Credit Card'],
            'category': categories['Entertainment'],
            'frequency': 'monthly',
            'start_date': datetime.now().date().replace(day=15),
            'next_due_date': datetime.now().date().replace(day=15) + relativedelta(months=1),
            'is_active': True
        },
    ]
    
    for recurring in recurring_data:
        rec_trans, created = RecurringTransaction.objects.get_or_create(
            user=demo_user,
            description=recurring['description'],
            defaults=recurring
        )
    print("✓ Sample recurring transactions created")
    
    # Create budgets for current month
    current_date = datetime.now().date()
    current_month = current_date.month
    current_year = current_date.year
    
    budget_data = [
        {'category': categories['Groceries'], 'amount': Decimal('400.00')},
        {'category': categories['Transportation'], 'amount': Decimal('300.00')},
        {'category': categories['Utilities'], 'amount': Decimal('200.00')},
        {'category': categories['Entertainment'], 'amount': Decimal('150.00')},
        {'category': categories['Dining Out'], 'amount': Decimal('250.00')},
        {'category': categories['Shopping'], 'amount': Decimal('200.00')},
        {'category': categories['Healthcare'], 'amount': Decimal('100.00')},
    ]
    
    for budget_item in budget_data:
        budget, created = Budget.objects.get_or_create(
            user=demo_user,
            category=budget_item['category'],
            month=current_month,
            year=current_year,
            defaults={'amount': budget_item['amount']}
        )
    print("✓ Sample budgets created")
    
    print("\n🎉 Sample data creation completed!")
    print("\nDemo login credentials:")
    print("Username: demo")
    print("Password: demo123")
    print("\nAdmin login credentials:")
    print("Username: admin")
    print("Password: admin123")
    print("\nYou can now start using the Finance Tracker application!")

if __name__ == '__main__':
    create_sample_data()
