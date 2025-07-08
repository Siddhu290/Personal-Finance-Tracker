from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from .models import Budget
from accounts.models import Category
from datetime import datetime


class BudgetForm(forms.ModelForm):
    """Form for creating/editing budgets"""
    
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Only show expense categories for budgets
            self.fields['category'].queryset = Category.objects.filter(
                user=self.user, 
                category_type='expense', 
                is_active=True
            )

        # Set default year to current year
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        self.fields['year'].initial = current_year
        self.fields['month'].initial = current_month
        
        # Generate year choices (current year ± 2)
        year_choices = [(year, year) for year in range(current_year - 2, current_year + 3)]
        self.fields['year'] = forms.ChoiceField(choices=year_choices, initial=current_year)
        
        # Month choices
        month_choices = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        self.fields['month'] = forms.ChoiceField(choices=month_choices, initial=current_month)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'category',
            Row(
                Column('amount', css_class='form-group col-md-4 mb-3'),
                Column('month', css_class='form-group col-md-4 mb-3'),
                Column('year', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Budget', css_class='btn btn-primary')
        )


class BulkBudgetForm(forms.Form):
    """Form for creating multiple budgets at once"""
    month = forms.ChoiceField(choices=[])
    year = forms.ChoiceField(choices=[])
    copy_from_month = forms.ChoiceField(choices=[], required=False, 
                                       help_text="Copy budgets from another month (optional)")
    copy_from_year = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up month and year choices
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        month_choices = [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        year_choices = [(year, year) for year in range(current_year - 2, current_year + 3)]
        
        self.fields['month'].choices = month_choices
        self.fields['year'].choices = year_choices
        self.fields['copy_from_month'].choices = [('', 'None')] + month_choices
        self.fields['copy_from_year'].choices = [('', 'None')] + year_choices
        
        self.fields['month'].initial = current_month
        self.fields['year'].initial = current_year

        # Add category fields dynamically
        if self.user:
            categories = Category.objects.filter(
                user=self.user, 
                category_type='expense', 
                is_active=True
            )
            
            for category in categories:
                field_name = f'category_{category.id}'
                self.fields[field_name] = forms.DecimalField(
                    max_digits=10,
                    decimal_places=2,
                    required=False,
                    min_value=0,
                    label=category.name,
                    widget=forms.NumberInput(attrs={'step': '0.01'})
                )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('month', css_class='form-group col-md-3 mb-3'),
                Column('year', css_class='form-group col-md-3 mb-3'),
                Column('copy_from_month', css_class='form-group col-md-3 mb-3'),
                Column('copy_from_year', css_class='form-group col-md-3 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Budgets', css_class='btn btn-primary')
        )


class BudgetFilterForm(forms.Form):
    """Form for filtering budgets"""
    month = forms.ChoiceField(choices=[], required=False)
    year = forms.ChoiceField(choices=[], required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False, empty_label="All Categories")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up month and year choices
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        month_choices = [('', 'All Months')] + [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ]
        year_choices = [('', 'All Years')] + [(year, year) for year in range(current_year - 5, current_year + 3)]
        
        self.fields['month'].choices = month_choices
        self.fields['year'].choices = year_choices
        self.fields['month'].initial = current_month
        self.fields['year'].initial = current_year
        
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(
                user=self.user, 
                category_type='expense', 
                is_active=True
            )

        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('month', css_class='form-group col-md-4 mb-3'),
                Column('year', css_class='form-group col-md-4 mb-3'),
                Column('category', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Filter', css_class='btn btn-primary')
        )
