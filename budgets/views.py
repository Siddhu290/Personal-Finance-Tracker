from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Avg
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from decimal import Decimal

from .models import Budget, BudgetAlert
from .forms import BudgetForm, BulkBudgetForm, BudgetFilterForm
from accounts.models import Category
from transactions.models import Transaction


class BudgetListView(LoginRequiredMixin, ListView):
    """List user's budgets with filtering"""
    model = Budget
    template_name = 'budgets/budget_list.html'
    context_object_name = 'budgets'
    paginate_by = 20

    def get_queryset(self):
        queryset = Budget.objects.filter(user=self.request.user).order_by('-year', '-month', 'category__name')
        
        # Apply filters
        form = BudgetFilterForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            if form.cleaned_data.get('month'):
                queryset = queryset.filter(month=form.cleaned_data['month'])
            
            if form.cleaned_data.get('year'):
                queryset = queryset.filter(year=form.cleaned_data['year'])
            
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category=form.cleaned_data['category'])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = BudgetFilterForm(self.request.GET, user=self.request.user)
        
        # Add summary statistics
        budgets = self.get_queryset()
        context['total_budgeted'] = budgets.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_spent = Decimal('0.00')
        over_budget_count = 0
        
        for budget in budgets:
            spent = budget.get_spent_amount()
            total_spent += spent
            if budget.is_over_budget():
                over_budget_count += 1
        
        context['total_spent'] = total_spent
        context['total_remaining'] = context['total_budgeted'] - total_spent
        context['over_budget_count'] = over_budget_count
        
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    """Create new budget"""
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Check if budget already exists for this category/month/year
        existing = Budget.objects.filter(
            user=self.request.user,
            category=form.cleaned_data['category'],
            month=form.cleaned_data['month'],
            year=form.cleaned_data['year']
        ).first()
        
        if existing:
            messages.error(self.request, 
                f'Budget for {form.cleaned_data["category"].name} in '
                f'{form.cleaned_data["month"]}/{form.cleaned_data["year"]} already exists.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Budget created successfully!')
        return super().form_valid(form)


class BudgetUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing budget"""
    model = Budget
    form_class = BudgetForm
    template_name = 'budgets/budget_form.html'
    success_url = reverse_lazy('budgets:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Budget updated successfully!')
        return super().form_valid(form)


class BudgetDeleteView(LoginRequiredMixin, DeleteView):
    """Delete budget"""
    model = Budget
    template_name = 'budgets/budget_confirm_delete.html'
    success_url = reverse_lazy('budgets:budget_list')

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        budget = self.get_object()
        messages.success(request, f'Budget for {budget.category.name} deleted successfully!')
        return super().delete(request, *args, **kwargs)


class BudgetOverviewView(LoginRequiredMixin, TemplateView):
    """Budget overview with charts and analytics"""
    template_name = 'budgets/budget_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Current month budgets
        current_budgets = Budget.objects.filter(
            user=user,
            year=current_year,
            month=current_month,
            is_active=True
        ).order_by('category__name')
        
        budget_data = []
        total_budgeted = Decimal('0.00')
        total_spent = Decimal('0.00')
        
        for budget in current_budgets:
            spent = budget.get_spent_amount()
            remaining = budget.get_remaining_amount()
            utilization = budget.get_utilization_percentage()
            
            budget_data.append({
                'budget': budget,
                'spent': spent,
                'remaining': remaining,
                'utilization': utilization,
                'status': 'danger' if utilization >= 100 else 'warning' if utilization >= 80 else 'success'
            })
            
            total_budgeted += budget.amount
            total_spent += spent
        
        # Monthly trends (last 6 months)
        monthly_trends = []
        for i in range(6):
            month_date = timezone.now().replace(day=1) - timezone.timedelta(days=30 * i)
            month_budgets = Budget.objects.filter(
                user=user,
                year=month_date.year,
                month=month_date.month
            )
            
            month_total = month_budgets.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            month_spent = Decimal('0.00')
            
            for budget in month_budgets:
                month_spent += budget.get_spent_amount()
            
            monthly_trends.append({
                'month': month_date.strftime('%B %Y'),
                'budgeted': float(month_total),
                'spent': float(month_spent),
                'saved': float(month_total - month_spent)
            })
        
        monthly_trends.reverse()
        
        context.update({
            'current_budgets': current_budgets,
            'budget_data': budget_data,
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'total_remaining': total_budgeted - total_spent,
            'monthly_trends': monthly_trends,
            'current_month': current_month,
            'current_year': current_year,
        })
        
        return context


class BudgetAnalysisView(LoginRequiredMixin, TemplateView):
    """Detailed budget analysis for specific month"""
    template_name = 'budgets/budget_analysis.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get year and month from URL parameters or default to current
        year = kwargs.get('year', timezone.now().year)
        month = kwargs.get('month', timezone.now().month)
        
        # Convert to integers if they're strings
        year = int(year)
        month = int(month)
        
        budgets = Budget.objects.filter(
            user=user,
            year=year,
            month=month
        ).order_by('category__name')
        
        analysis_data = []
        total_budgeted = Decimal('0.00')
        total_spent = Decimal('0.00')
        
        for budget in budgets:
            spent = budget.get_spent_amount()
            daily_transactions = Transaction.objects.filter(
                user=user,
                category=budget.category,
                transaction_type='expense',
                date__year=year,
                date__month=month
            ).order_by('date')
            
            analysis_data.append({
                'budget': budget,
                'spent': spent,
                'remaining': budget.get_remaining_amount(),
                'utilization': budget.get_utilization_percentage(),
                'daily_transactions': daily_transactions,
                'transaction_count': daily_transactions.count(),
                'avg_transaction': daily_transactions.aggregate(avg=Avg('amount'))['avg'] or Decimal('0.00')
            })
            
            total_budgeted += budget.amount
            total_spent += spent
        
        context.update({
            'budgets': budgets,
            'analysis_data': analysis_data,
            'total_budgeted': total_budgeted,
            'total_spent': total_spent,
            'year': year,
            'month': month,
            'month_name': datetime(year, month, 1).strftime('%B'),
        })
        
        return context


class BudgetAlertListView(LoginRequiredMixin, ListView):
    """List budget alerts"""
    model = BudgetAlert
    template_name = 'budgets/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 20

    def get_queryset(self):
        return BudgetAlert.objects.filter(user=self.request.user).order_by('-created_at')


@login_required
def mark_alert_read(request, pk):
    """Mark budget alert as read"""
    alert = get_object_or_404(BudgetAlert, pk=pk, user=request.user)
    alert.is_read = True
    alert.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Alert marked as read.')
    return redirect('budgets:alert_list')


@login_required
def get_budget_data(request, year, month):
    """API endpoint for budget chart data"""
    budgets = Budget.objects.filter(
        user=request.user,
        year=year,
        month=month
    )
    
    data = {
        'labels': [],
        'budgeted': [],
        'spent': [],
        'colors': []
    }
    
    for budget in budgets:
        data['labels'].append(budget.category.name)
        data['budgeted'].append(float(budget.amount))
        data['spent'].append(float(budget.get_spent_amount()))
        data['colors'].append(budget.category.color)
    
    return JsonResponse(data)
