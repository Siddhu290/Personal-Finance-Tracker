from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from transactions.models import Transaction
from accounts.models import Account, Category
from budgets.models import Budget


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    """Main reports dashboard"""
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get current period data
        current_year = timezone.now().year
        current_month = timezone.now().month
        
        # Basic stats
        total_transactions = Transaction.objects.filter(user=user).count()
        total_income = Transaction.objects.filter(
            user=user, transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_expenses = Transaction.objects.filter(
            user=user, transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:5]
        
        # Top spending categories
        top_categories = Transaction.objects.filter(
            user=user, 
            transaction_type='expense'
        ).values('category__name').annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        context.update({
            'total_transactions': total_transactions,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_worth': total_income - total_expenses,
            'current_year': current_year,
            'current_month': current_month,
            'recent_transactions': recent_transactions,
            'top_categories': top_categories,
        })
        
        return context


class IncomeExpenseReportView(LoginRequiredMixin, TemplateView):
    """Income vs expenses analysis"""
    template_name = 'reports/income_expenses.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get date range from query params or default to last 12 months
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=365)
        
        if self.request.GET.get('start_date'):
            start_date = datetime.strptime(self.request.GET['start_date'], '%Y-%m-%d').date()
        if self.request.GET.get('end_date'):
            end_date = datetime.strptime(self.request.GET['end_date'], '%Y-%m-%d').date()
        
        # Monthly income/expense data for the chart
        monthly_data = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_income = Transaction.objects.filter(
                user=user,
                transaction_type='income',
                date__year=current_date.year,
                date__month=current_date.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_expenses = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__year=current_date.year,
                date__month=current_date.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_data.append({
                'month': current_date.strftime('%Y-%m'),
                'month_name': current_date.strftime('%B %Y'),
                'income': float(month_income),
                'expenses': float(month_expenses),
                'net': float(month_income - month_expenses)
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Summary statistics
        total_income = sum(item['income'] for item in monthly_data)
        total_expenses = sum(item['expenses'] for item in monthly_data)
        net_income = total_income - total_expenses
        
        # Chart data
        monthly_labels = [item['month_name'] for item in monthly_data]
        monthly_income = [item['income'] for item in monthly_data]
        monthly_expenses = [item['expenses'] for item in monthly_data]
        
        # Daily data for trend chart
        daily_data = []
        daily_labels = []
        daily_income = []
        daily_expenses = []
        
        current_date = start_date
        while current_date <= end_date:
            day_income = Transaction.objects.filter(
                user=user,
                transaction_type='income',
                date=current_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            day_expenses = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date=current_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_labels.append(current_date.strftime('%m/%d'))
            daily_income.append(float(day_income))
            daily_expenses.append(float(day_expenses))
            
            current_date += timedelta(days=1)
        
        context.update({
            'monthly_data': monthly_data,
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_income': json.dumps(monthly_income),
            'monthly_expenses': json.dumps(monthly_expenses),
            'daily_labels': json.dumps(daily_labels),
            'daily_income': json.dumps(daily_income),
            'daily_expenses': json.dumps(daily_expenses),
            'total_income': Decimal(str(total_income)),
            'total_expenses': Decimal(str(total_expenses)),
            'net_income': Decimal(str(net_income)),
            'date_from': start_date,
            'date_to': end_date,
        })
        
        return context


class CategoryAnalysisView(LoginRequiredMixin, TemplateView):
    """Category-wise spending analysis"""
    template_name = 'reports/category_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get date range
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=365)
        
        if self.request.GET.get('start_date'):
            start_date = datetime.strptime(self.request.GET['start_date'], '%Y-%m-%d').date()
        if self.request.GET.get('end_date'):
            end_date = datetime.strptime(self.request.GET['end_date'], '%Y-%m-%d').date()
        
        # Expense categories analysis
        expense_categories = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        ).order_by('-total')
        
        # Income categories analysis
        income_categories = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount'),
            count=Count('id'),
            avg=Avg('amount')
        ).order_by('-total')
        
        # Prepare chart data
        expense_chart_data = {
            'labels': [cat['category__name'] for cat in expense_categories],
            'data': [float(cat['total']) for cat in expense_categories],
            'colors': [cat['category__color'] or '#3B82F6' for cat in expense_categories],
        }
        
        income_chart_data = {
            'labels': [cat['category__name'] for cat in income_categories],
            'data': [float(cat['total']) for cat in income_categories],
            'colors': [cat['category__color'] or '#10B981' for cat in income_categories],
        }
        
        # Calculate total for percentages
        total_expenses = sum(float(cat['total']) for cat in expense_categories)
        
        # Add percentage and transaction count to categories
        top_categories = []
        for cat in expense_categories[:10]:
            percentage = (float(cat['total']) / total_expenses * 100) if total_expenses > 0 else 0
            top_categories.append({
                'name': cat['category__name'],
                'color': cat['category__color'] or '#3B82F6',
                'icon': 'fas fa-tag',  # Default icon
                'total': cat['total'],
                'transaction_count': cat['count'],
                'percentage': percentage
            })
        
        # Transaction type filter
        transaction_type = self.request.GET.get('transaction_type', '')
        
        context.update({
            'date_from': start_date,
            'date_to': end_date,
            'transaction_type': transaction_type,
            'top_categories': top_categories,
            'category_labels': json.dumps([cat['category__name'] for cat in expense_categories]),
            'category_values': json.dumps([float(cat['total']) for cat in expense_categories]),
            'category_colors': json.dumps([cat['category__color'] or '#3B82F6' for cat in expense_categories]),
            'trend_labels': json.dumps(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']),  # Placeholder
            'trend_datasets': json.dumps([]),  # Placeholder
        })
        
        return context


class TrendsReportView(LoginRequiredMixin, TemplateView):
    """Trends and patterns analysis"""
    template_name = 'reports/trends.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Last 6 months trends
        end_date = timezone.now().date()
        start_date = end_date.replace(day=1) - timedelta(days=180)
        
        # Monthly spending trends
        monthly_trends = []
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_total = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__year=current_date.year,
                date__month=current_date.month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_trends.append({
                'month': current_date.strftime('%B %Y'),
                'total': float(month_total)
            })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        # Daily spending patterns (day of week)
        daily_patterns = []
        for day in range(7):  # 0=Monday, 6=Sunday
            day_total = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__week_day=(day + 2) % 7 + 1  # Django uses 1=Sunday
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_patterns.append({
                'day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day],
                'total': float(day_total)
            })
        
        context.update({
            'monthly_trends': json.dumps(monthly_trends),
            'daily_patterns': json.dumps(daily_patterns),
            'start_date': start_date,
            'end_date': end_date,
        })
        
        return context


class MonthlyReportView(LoginRequiredMixin, TemplateView):
    """Monthly report for specific month"""
    template_name = 'reports/monthly_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get month/year from URL or default to current month
        year = int(kwargs.get('year', timezone.now().year))
        month = int(kwargs.get('month', timezone.now().month))
        
        # Calculate date range for the month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Get transactions for the month
        transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('-date')
        
        # Calculate totals
        month_income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
        month_expenses = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Category breakdown
        category_breakdown = transactions.filter(transaction_type='expense').values(
            'category__name', 'category__color', 'category__icon'
        ).annotate(
            total=Sum('amount'),
            percentage=Sum('amount') * 100.0 / month_expenses if month_expenses > 0 else 0
        ).order_by('-total')
        
        # Navigation months
        prev_month_date = start_date - timedelta(days=1)
        next_month_date = end_date + timedelta(days=1)
        
        # Daily spending for chart
        daily_spending = []
        daily_labels = []
        current_date = start_date
        while current_date <= end_date:
            day_expenses = transactions.filter(
                transaction_type='expense',
                date=current_date
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            daily_spending.append(float(day_expenses))
            daily_labels.append(current_date.strftime('%d'))
            current_date += timedelta(days=1)
        
        # Budget data if available
        budgets = Budget.objects.filter(
            user=user,
            year=year,
            month=month,
            is_active=True
        )
        
        budget_data = []
        for budget in budgets:
            spent = transactions.filter(
                transaction_type='expense',
                category=budget.category
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            budget_data.append({
                'category': budget.category,
                'amount': budget.amount,
                'spent': spent,
                'remaining': budget.amount - spent,
                'percentage': min(100, float(spent / budget.amount * 100)) if budget.amount > 0 else 0,
                'over_budget': spent > budget.amount,
                'over_amount': spent - budget.amount if spent > budget.amount else Decimal('0.00')
            })
        
        context.update({
            'year': year,
            'month': month,
            'month_name': start_date.strftime('%B %Y'),
            'month': start_date,
            'start_date': start_date,
            'end_date': end_date,
            'recent_transactions': transactions[:10],
            'total_income': month_income,
            'total_expenses': month_expenses,
            'net_income': month_income - month_expenses,
            'savings_rate': float(month_income - month_expenses) / float(month_income) * 100 if month_income > 0 else 0,
            'expense_categories': category_breakdown,
            'daily_spending': json.dumps(daily_spending),
            'daily_labels': json.dumps(daily_labels),
            'budgets': budget_data,
            'prev_month': prev_month_date,
            'next_month': next_month_date,
        })
        
        return context


class YearlyReportView(LoginRequiredMixin, TemplateView):
    """Yearly report for specific year"""
    template_name = 'reports/yearly_report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get year from URL or default to current year
        year = int(kwargs.get('year', timezone.now().year))
        
        # Calculate date range for the year
        start_date = datetime(year, 1, 1).date()
        end_date = datetime(year, 12, 31).date()
        
        # Monthly breakdown for the year
        monthly_breakdown = []
        for month in range(1, 13):
            month_income = Transaction.objects.filter(
                user=user,
                transaction_type='income',
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            month_expenses = Transaction.objects.filter(
                user=user,
                transaction_type='expense',
                date__year=year,
                date__month=month
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            monthly_breakdown.append({
                'year': year,
                'month': month,
                'date': datetime(year, month, 1).date(),
                'month_name': datetime(year, month, 1).strftime('%B'),
                'income': month_income,
                'expenses': month_expenses,
                'net': month_income - month_expenses,
                'savings_rate': float(month_income - month_expenses) / float(month_income) * 100 if month_income > 0 else 0,
                'top_category': 'N/A'  # Placeholder
            })
        
        # Year totals
        year_income = sum(m['income'] for m in monthly_breakdown)
        year_expenses = sum(m['expenses'] for m in monthly_breakdown)
        net_income = year_income - year_expenses
        
        # Navigation years
        prev_year = year - 1
        next_year = year + 1
        
        # Chart data
        monthly_labels = [m['month_name'] for m in monthly_breakdown]
        monthly_income_data = [float(m['income']) for m in monthly_breakdown]
        monthly_expenses_data = [float(m['expenses']) for m in monthly_breakdown]
        monthly_net_data = [float(m['net']) for m in monthly_breakdown]
        
        # Top categories for the year
        top_expense_categories = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__color', 'category__icon').annotate(
            total=Sum('amount'),
            transaction_count=Count('id'),
            monthly_avg=Sum('amount') / 12
        ).order_by('-total')[:5]
        
        top_income_categories = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__color', 'category__icon').annotate(
            total=Sum('amount'),
            transaction_count=Count('id'),
            monthly_avg=Sum('amount') / 12
        ).order_by('-total')[:5]
        
        # Category chart data
        category_labels = [cat['category__name'] for cat in top_expense_categories]
        category_values = [float(cat['total']) for cat in top_expense_categories]
        category_colors = [cat['category__color'] or '#6366f1' for cat in top_expense_categories]
        
        context.update({
            'year': year,
            'prev_year': prev_year,
            'next_year': next_year,
            'start_date': start_date,
            'end_date': end_date,
            'monthly_breakdown': monthly_breakdown,
            'total_income': year_income,
            'total_expenses': year_expenses,
            'net_income': net_income,
            'avg_monthly_income': year_income / 12 if year_income else Decimal('0.00'),
            'avg_monthly_expenses': year_expenses / 12 if year_expenses else Decimal('0.00'),
            'avg_monthly_net': net_income / 12 if net_income else Decimal('0.00'),
            'savings_rate': float(net_income / year_income * 100) if year_income > 0 else 0,
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_income': json.dumps(monthly_income_data),
            'monthly_expenses': json.dumps(monthly_expenses_data),
            'monthly_net': json.dumps(monthly_net_data),
            'category_labels': json.dumps(category_labels),
            'category_values': json.dumps(category_values),
            'category_colors': json.dumps(category_colors),
            'top_expense_categories': top_expense_categories,
            'top_income_categories': top_income_categories,
        })
        
        return context


class AccountSummaryView(LoginRequiredMixin, TemplateView):
    """Account summary and balances"""
    template_name = 'reports/account_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get all user accounts with their current balances
        accounts = Account.objects.filter(user=user)
        
        account_data = []
        total_balance = Decimal('0.00')
        
        # Account type totals
        banking_total = Decimal('0.00')
        banking_count = 0
        credit_total = Decimal('0.00')
        credit_count = 0
        investment_total = Decimal('0.00')
        investment_count = 0
        cash_total = Decimal('0.00')
        cash_count = 0
        
        for account in accounts:
            current_balance = account.balance
            total_balance += current_balance
            
            # Add to type totals
            if account.account_type in ['checking', 'savings']:
                banking_total += current_balance
                banking_count += 1
            elif account.account_type == 'credit_card':
                credit_total += current_balance
                credit_count += 1
            elif account.account_type == 'investment':
                investment_total += current_balance
                investment_count += 1
            elif account.account_type == 'cash':
                cash_total += current_balance
                cash_count += 1
            
            # Add utilization for credit cards
            utilization = 0
            if account.account_type == 'credit_card' and hasattr(account, 'credit_limit') and account.credit_limit:
                utilization = min(100, abs(float(current_balance) / float(account.credit_limit) * 100))
            
            # Recent transaction count
            recent_transaction_count = Transaction.objects.filter(
                user=user, 
                account=account,
                date__gte=timezone.now().date() - timedelta(days=30)
            ).count()
            
            account_data.append({
                'account': account,
                'current_balance': current_balance,
                'utilization': utilization,
                'recent_transaction_count': recent_transaction_count,
            })
        
        # Chart data
        account_labels = [acc['account'].name for acc in account_data]
        account_balances = [float(acc['current_balance']) for acc in account_data]
        
        type_labels = ['Banking', 'Credit Cards', 'Investments', 'Cash']
        type_balances = [float(banking_total), float(credit_total), float(investment_total), float(cash_total)]
        
        # Balance change (placeholder - would need historical data)
        balance_change = Decimal('0.00')
        
        # History data (placeholder)
        history_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        history_balances = [float(total_balance)] * 6
        
        context.update({
            'accounts': account_data,
            'total_balance': total_balance,
            'balance_change': balance_change,
            'banking_total': banking_total,
            'banking_count': banking_count,
            'credit_total': credit_total,
            'credit_count': credit_count,
            'investment_total': investment_total,
            'investment_count': investment_count,
            'cash_total': cash_total,
            'cash_count': cash_count,
            'account_labels': json.dumps(account_labels),
            'account_balances': json.dumps(account_balances),
            'type_labels': json.dumps(type_labels),
            'type_balances': json.dumps(type_balances),
            'history_labels': json.dumps(history_labels),
            'history_balances': json.dumps(history_balances),
        })
        
        return context


# API endpoints for chart data
@login_required
def get_income_expense_chart_data(request):
    """API endpoint for income/expense chart data"""
    user = request.user
    
    # Get last 12 months
    end_date = timezone.now().date()
    start_date = end_date.replace(day=1) - timedelta(days=365)
    
    monthly_data = []
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        month_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__year=current_date.year,
            date__month=current_date.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__year=current_date.year,
            date__month=current_date.month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        monthly_data.append({
            'month': current_date.strftime('%B %Y'),
            'income': float(month_income),
            'expenses': float(month_expenses)
        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return JsonResponse({'data': monthly_data})


@login_required
def get_category_pie_chart_data(request):
    """API endpoint for category pie chart data"""
    user = request.user
    transaction_type = request.GET.get('type', 'expense')
    
    # Get last 3 months
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=90)
    
    categories = Transaction.objects.filter(
        user=user,
        transaction_type=transaction_type,
        date__range=[start_date, end_date]
    ).values('category__name', 'category__color').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    data = {
        'labels': [cat['category__name'] for cat in categories],
        'data': [float(cat['total']) for cat in categories],
        'colors': [cat['category__color'] or '#3B82F6' for cat in categories]
    }
    
    return JsonResponse(data)


@login_required
def get_trends_chart_data(request):
    """API endpoint for trends chart data"""
    user = request.user
    
    # Daily spending for last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        day_total = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date=current_date
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'total': float(day_total)
        })
        
        current_date += timedelta(days=1)
    
    return JsonResponse({'data': daily_data})


@login_required
def get_account_balance_chart_data(request):
    """API endpoint for account balance chart data"""
    user = request.user
    
    accounts = Account.objects.filter(user=user)
    account_data = []
    
    for account in accounts:
        # Calculate current balance
        income = Transaction.objects.filter(
            user=user,
            account=account,
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        expenses = Transaction.objects.filter(
            user=user,
            account=account,
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        current_balance = account.balance
        
        account_data.append({
            'name': account.name,
            'balance': float(current_balance),
            'type': account.account_type
        })
    
    return JsonResponse({'data': account_data})
