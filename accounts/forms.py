from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import UserProfile, Account, Category


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Account', css_class='btn btn-primary w-100')
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(user=user)
        return user


class CustomLoginForm(AuthenticationForm):
    """Custom login form with styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            Submit('submit', 'Login', css_class='btn btn-primary w-100')
        )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['currency', 'dark_mode', 'email_notifications', 'budget_alerts']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('currency', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('dark_mode', css_class='form-group col-md-4 mb-3'),
                Column('email_notifications', css_class='form-group col-md-4 mb-3'),
                Column('budget_alerts', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if self.user and commit:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            self.user.save()
        return profile


class AccountForm(forms.ModelForm):
    """Form for creating/editing accounts"""
    
    class Meta:
        model = Account
        fields = ['name', 'account_type', 'balance']
        widgets = {
            'balance': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('account_type', css_class='form-group col-md-6 mb-3'),
                Column('balance', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Account', css_class='btn btn-primary')
        )


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'color', 'icon']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            Row(
                Column('category_type', css_class='form-group col-md-4 mb-3'),
                Column('color', css_class='form-group col-md-4 mb-3'),
                Column('icon', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )
