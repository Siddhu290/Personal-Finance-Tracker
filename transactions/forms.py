from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Transaction, RecurringTransaction
from accounts.models import Account, Category


class TransactionForm(forms.ModelForm):
    """Form for creating/editing transactions"""
    
    class Meta:
        model = Transaction
        fields = ['account', 'category', 'transaction_type', 'amount', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['account'].queryset = Account.objects.filter(user=self.user, is_active=True)
            self.fields['category'].queryset = Category.objects.filter(user=self.user, is_active=True)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('account', css_class='form-group col-md-6 mb-3'),
                Column('category', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('transaction_type', css_class='form-group col-md-4 mb-3'),
                Column('amount', css_class='form-group col-md-4 mb-3'),
                Column('date', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            'description',
            Submit('submit', 'Save Transaction', css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')
        category = cleaned_data.get('category')
        
        if transaction_type and category:
            if transaction_type == 'income' and category.category_type != 'income':
                raise forms.ValidationError("Income transactions must use income categories.")
            elif transaction_type == 'expense' and category.category_type != 'expense':
                raise forms.ValidationError("Expense transactions must use expense categories.")
        
        return cleaned_data


class TransferForm(forms.Form):
    """Form for transferring money between accounts"""
    from_account = forms.ModelChoiceField(queryset=Account.objects.none())
    to_account = forms.ModelChoiceField(queryset=Account.objects.none())
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    description = forms.CharField(max_length=200, initial="Transfer between accounts")
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        # Remove instance from kwargs as Form doesn't accept it
        kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            accounts = Account.objects.filter(user=self.user, is_active=True)
            self.fields['from_account'].queryset = accounts
            self.fields['to_account'].queryset = accounts

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('from_account', css_class='form-group col-md-6 mb-3'),
                Column('to_account', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('amount', css_class='form-group col-md-6 mb-3'),
                Column('date', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'description',
            Submit('submit', 'Transfer Funds', css_class='btn btn-primary')
        )

    def clean(self):
        cleaned_data = super().clean()
        from_account = cleaned_data.get('from_account')
        to_account = cleaned_data.get('to_account')
        
        if from_account and to_account and from_account == to_account:
            raise forms.ValidationError("Cannot transfer to the same account.")
        
        return cleaned_data


class RecurringTransactionForm(forms.ModelForm):
    """Form for creating/editing recurring transactions"""
    
    class Meta:
        model = RecurringTransaction
        fields = ['account', 'category', 'transaction_type', 'amount', 'description', 
                 'frequency', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['account'].queryset = Account.objects.filter(user=self.user, is_active=True)
            self.fields['category'].queryset = Category.objects.filter(user=self.user, is_active=True)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('account', css_class='form-group col-md-6 mb-3'),
                Column('category', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('transaction_type', css_class='form-group col-md-4 mb-3'),
                Column('amount', css_class='form-group col-md-4 mb-3'),
                Column('frequency', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-3'),
                Column('end_date', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'description',
            Submit('submit', 'Save Recurring Transaction', css_class='btn btn-primary')
        )


class TransactionSearchForm(forms.Form):
    """Form for searching and filtering transactions"""
    search = forms.CharField(max_length=200, required=False, 
                           widget=forms.TextInput(attrs={'placeholder': 'Search transactions...'}))
    account = forms.ModelChoiceField(queryset=Account.objects.none(), required=False, empty_label="All Accounts")
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False, empty_label="All Categories")
    transaction_type = forms.ChoiceField(choices=[('', 'All Types')] + Transaction.TRANSACTION_TYPES, required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    amount_min = forms.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=0)
    amount_max = forms.DecimalField(max_digits=10, decimal_places=2, required=False, min_value=0)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['account'].queryset = Account.objects.filter(user=self.user, is_active=True)
            self.fields['category'].queryset = Category.objects.filter(user=self.user, is_active=True)

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-3'),
                Column('account', css_class='form-group col-md-4 mb-3'),
                Column('category', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('transaction_type', css_class='form-group col-md-4 mb-3'),
                Column('date_from', css_class='form-group col-md-4 mb-3'),
                Column('date_to', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('amount_min', css_class='form-group col-md-6 mb-3'),
                Column('amount_max', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Search', css_class='btn btn-primary me-2'),
            HTML('<a href="{% url "transactions:transaction_list" %}" class="btn btn-secondary">Clear</a>')
        )


class ImportTransactionsForm(forms.Form):
    """Form for importing transactions from CSV/Excel"""
    file = forms.FileField(
        help_text="Upload a CSV or Excel file with columns: Date, Description, Amount, Account, Category, Type"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'file',
            Submit('submit', 'Import Transactions', css_class='btn btn-primary')
        )
