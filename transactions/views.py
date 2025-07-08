from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import pandas as pd
from io import BytesIO

from .models import Transaction, RecurringTransaction, TransactionReminder
from .forms import TransactionForm, TransferForm, RecurringTransactionForm, TransactionSearchForm, ImportTransactionsForm
from accounts.models import Account, Category
from budgets.models import Budget


class DashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard showing financial overview"""
    template_name = 'transactions/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get current month data
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Calculate totals
        total_income = Transaction.objects.filter(
            user=user, 
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        total_expenses = Transaction.objects.filter(
            user=user, 
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        current_month_income = Transaction.objects.filter(
            user=user,
            transaction_type='income',
            date__year=current_year,
            date__month=current_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        current_month_expenses = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            date__year=current_year,
            date__month=current_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Get account balances
        accounts = Account.objects.filter(user=user, is_active=True)
        total_balance = accounts.aggregate(total=Sum('balance'))['total'] or Decimal('0.00')
        
        # Recent transactions
        recent_transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:10]
        
        # Upcoming recurring transactions
        upcoming_recurring = RecurringTransaction.objects.filter(
            user=user,
            is_active=True,
            next_due_date__lte=timezone.now().date() + timedelta(days=7)
        ).order_by('next_due_date')[:5]
        
        # Budget alerts
        current_budgets = Budget.objects.filter(
            user=user,
            year=current_year,
            month=current_month,
            is_active=True
        )
        
        budget_alerts = []
        for budget in current_budgets:
            utilization = budget.get_utilization_percentage()
            if utilization >= 80:
                budget_alerts.append({
                    'budget': budget,
                    'utilization': utilization,
                    'type': 'danger' if utilization >= 100 else 'warning'
                })
        
        context.update({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_worth': total_income - total_expenses,
            'current_month_income': current_month_income,
            'current_month_expenses': current_month_expenses,
            'current_month_net': current_month_income - current_month_expenses,
            'total_balance': total_balance,
            'accounts': accounts,
            'recent_transactions': recent_transactions,
            'upcoming_recurring': upcoming_recurring,
            'budget_alerts': budget_alerts,
        })
        
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    """List all transactions with filtering"""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        queryset = Transaction.objects.filter(user=self.request.user).order_by('-date', '-created_at')
        
        # Apply filters from search form
        form = TransactionSearchForm(self.request.GET, user=self.request.user)
        if form.is_valid():
            if form.cleaned_data.get('search'):
                queryset = queryset.filter(
                    Q(description__icontains=form.cleaned_data['search']) |
                    Q(account__name__icontains=form.cleaned_data['search'])
                )
            
            if form.cleaned_data.get('account'):
                queryset = queryset.filter(account=form.cleaned_data['account'])
            
            if form.cleaned_data.get('category'):
                queryset = queryset.filter(category=form.cleaned_data['category'])
            
            if form.cleaned_data.get('transaction_type'):
                queryset = queryset.filter(transaction_type=form.cleaned_data['transaction_type'])
            
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(date__gte=form.cleaned_data['date_from'])
            
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(date__lte=form.cleaned_data['date_to'])
            
            if form.cleaned_data.get('amount_min'):
                queryset = queryset.filter(amount__gte=form.cleaned_data['amount_min'])
            
            if form.cleaned_data.get('amount_max'):
                queryset = queryset.filter(amount__lte=form.cleaned_data['amount_max'])
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = TransactionSearchForm(self.request.GET, user=self.request.user)
        return context


class TransactionCreateView(LoginRequiredMixin, CreateView):
    """Create new transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Update account balance
        transaction = form.save()
        account = transaction.account
        
        if transaction.transaction_type == 'income':
            account.balance += transaction.amount
        elif transaction.transaction_type == 'expense':
            account.balance -= transaction.amount
        
        account.save()
        
        messages.success(self.request, 'Transaction created successfully!')
        return super().form_valid(form)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    """View transaction details"""
    model = Transaction
    template_name = 'transactions/transaction_detail.html'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing transaction"""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Revert old transaction from account balance
        old_transaction = Transaction.objects.get(pk=self.object.pk)
        account = old_transaction.account
        
        if old_transaction.transaction_type == 'income':
            account.balance -= old_transaction.amount
        elif old_transaction.transaction_type == 'expense':
            account.balance += old_transaction.amount
        
        # Apply new transaction to account balance
        new_transaction = form.save()
        if new_transaction.account != account:
            # Handle account change
            account.save()
            account = new_transaction.account
        
        if new_transaction.transaction_type == 'income':
            account.balance += new_transaction.amount
        elif new_transaction.transaction_type == 'expense':
            account.balance -= new_transaction.amount
        
        account.save()
        
        messages.success(self.request, 'Transaction updated successfully!')
        return super().form_valid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete transaction"""
    model = Transaction
    template_name = 'transactions/transaction_confirm_delete.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        transaction = self.get_object()
        account = transaction.account
        
        # Revert transaction from account balance
        if transaction.transaction_type == 'income':
            account.balance -= transaction.amount
        elif transaction.transaction_type == 'expense':
            account.balance += transaction.amount
        
        account.save()
        
        messages.success(request, 'Transaction deleted successfully!')
        return super().delete(request, *args, **kwargs)


class TransferCreateView(LoginRequiredMixin, CreateView):
    """Create transfer between accounts"""
    form_class = TransferForm
    template_name = 'transactions/transfer_form.html'
    success_url = reverse_lazy('transactions:transaction_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Create two transactions for the transfer
        from_account = form.cleaned_data['from_account']
        to_account = form.cleaned_data['to_account']
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']
        date = form.cleaned_data['date']
        
        # Create outgoing transaction
        Transaction.objects.create(
            user=self.request.user,
            account=from_account,
            transaction_type='transfer',
            amount=amount,
            description=f"{description} (to {to_account.name})",
            date=date,
            to_account=to_account
        )
        
        # Create incoming transaction
        Transaction.objects.create(
            user=self.request.user,
            account=to_account,
            transaction_type='transfer',
            amount=amount,
            description=f"{description} (from {from_account.name})",
            date=date
        )
        
        # Update account balances
        from_account.balance -= amount
        to_account.balance += amount
        from_account.save()
        to_account.save()
        
        messages.success(self.request, f'Transfer of ${amount} completed successfully!')
        return redirect(self.success_url)


class RecurringTransactionListView(LoginRequiredMixin, ListView):
    """List recurring transactions"""
    model = RecurringTransaction
    template_name = 'transactions/recurring_list.html'
    context_object_name = 'recurring_transactions'

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user).order_by('next_due_date')


class RecurringTransactionCreateView(LoginRequiredMixin, CreateView):
    """Create recurring transaction"""
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'transactions/recurring_form.html'
    success_url = reverse_lazy('transactions:recurring_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.next_due_date = form.cleaned_data['start_date']
        messages.success(self.request, 'Recurring transaction created successfully!')
        return super().form_valid(form)


class RecurringTransactionUpdateView(LoginRequiredMixin, UpdateView):
    """Update recurring transaction"""
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'transactions/recurring_form.html'
    success_url = reverse_lazy('transactions:recurring_list')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Recurring transaction updated successfully!')
        return super().form_valid(form)


class RecurringTransactionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete recurring transaction"""
    model = RecurringTransaction
    template_name = 'transactions/recurring_confirm_delete.html'
    success_url = reverse_lazy('transactions:recurring_list')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)


class ExecuteRecurringTransactionView(LoginRequiredMixin, TemplateView):
    """Execute a recurring transaction"""
    template_name = 'transactions/recurring_execute.html'

    def post(self, request, pk):
        recurring = get_object_or_404(RecurringTransaction, pk=pk, user=request.user)
        
        # Create the transaction
        transaction = Transaction.objects.create(
            user=request.user,
            account=recurring.account,
            category=recurring.category,
            transaction_type=recurring.transaction_type,
            amount=recurring.amount,
            description=recurring.description,
            date=timezone.now().date()
        )
        
        # Update account balance
        if transaction.transaction_type == 'income':
            recurring.account.balance += transaction.amount
        elif transaction.transaction_type == 'expense':
            recurring.account.balance -= transaction.amount
        recurring.account.save()
        
        # Update next due date
        from dateutil.relativedelta import relativedelta
        if recurring.frequency == 'daily':
            recurring.next_due_date += timedelta(days=1)
        elif recurring.frequency == 'weekly':
            recurring.next_due_date += timedelta(weeks=1)
        elif recurring.frequency == 'monthly':
            recurring.next_due_date += relativedelta(months=1)
        elif recurring.frequency == 'quarterly':
            recurring.next_due_date += relativedelta(months=3)
        elif recurring.frequency == 'yearly':
            recurring.next_due_date += relativedelta(years=1)
        
        recurring.save()
        
        messages.success(request, f'Recurring transaction "{recurring.description}" executed successfully!')
        return redirect('transactions:recurring_list')


class TransactionSearchView(TransactionListView):
    """Search transactions (inherits from TransactionListView)"""
    template_name = 'transactions/transaction_search.html'


class ImportTransactionsView(LoginRequiredMixin, TemplateView):
    """Import transactions from CSV/Excel"""
    template_name = 'transactions/import_transactions.html'

    def post(self, request):
        form = ImportTransactionsForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                imported_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # Assume columns: Date, Description, Amount, Account, Category, Type
                        account = Account.objects.get(user=request.user, name=row['Account'])
                        category = Category.objects.get(user=request.user, name=row['Category'])
                        
                        Transaction.objects.create(
                            user=request.user,
                            account=account,
                            category=category,
                            transaction_type=row['Type'].lower(),
                            amount=abs(float(row['Amount'])),
                            description=row['Description'],
                            date=pd.to_datetime(row['Date']).date()
                        )
                        imported_count += 1
                    except Exception as e:
                        errors.append(f"Row {index + 1}: {str(e)}")
                
                if imported_count > 0:
                    messages.success(request, f'Successfully imported {imported_count} transactions.')
                
                if errors:
                    messages.warning(request, f'Errors occurred: {"; ".join(errors[:5])}')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
        
        return render(request, self.template_name, {'form': form})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ImportTransactionsForm()
        return context


class ExportTransactionsView(LoginRequiredMixin, TemplateView):
    """Export transactions to CSV/Excel"""
    
    def get(self, request):
        format_type = request.GET.get('format', 'csv')
        
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')
        
        if format_type == 'excel':
            # Create Excel file
            output = BytesIO()
            df = pd.DataFrame(list(transactions.values(
                'date', 'description', 'amount', 'transaction_type',
                'account__name', 'category__name'
            )))
            df.columns = ['Date', 'Description', 'Amount', 'Type', 'Account', 'Category']
            df.to_excel(output, index=False)
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
        else:
            # Create CSV file
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Date', 'Description', 'Amount', 'Type', 'Account', 'Category'])
            
            for transaction in transactions:
                writer.writerow([
                    transaction.date,
                    transaction.description,
                    transaction.amount,
                    transaction.transaction_type,
                    transaction.account.name,
                    transaction.category.name if transaction.category else ''
                ])
        
        return response


@login_required
def get_account_balance(request, account_id):
    """API endpoint to get account balance"""
    try:
        account = Account.objects.get(id=account_id, user=request.user)
        return JsonResponse({'balance': float(account.balance)})
    except Account.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)


@login_required
def download_sample_csv(request):
    """Download a sample CSV file for import"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sample_transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Description', 'Amount', 'Type', 'Account', 'Category'])
    
    # Add sample data
    writer.writerow(['2024-01-01', 'Salary Payment', '5000.00', 'income', 'Checking Account', 'Salary'])
    writer.writerow(['2024-01-02', 'Grocery Shopping', '150.00', 'expense', 'Checking Account', 'Groceries'])
    writer.writerow(['2024-01-03', 'Gas Station', '45.00', 'expense', 'Credit Card', 'Transportation'])
    writer.writerow(['2024-01-04', 'Coffee Shop', '12.50', 'expense', 'Checking Account', 'Dining'])
    writer.writerow(['2024-01-05', 'Transfer to Savings', '1000.00', 'expense', 'Checking Account', 'Transfer'])
    
    return response
