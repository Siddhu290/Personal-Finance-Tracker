from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from .models import UserProfile, Account, Category
from .forms import CustomUserCreationForm, CustomLoginForm, UserProfileForm, AccountForm, CategoryForm
from django.views import View


class CustomLoginView(LoginView):
    """Custom login view with styled form"""
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('transactions:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        
        # Create default categories
        self.create_default_categories(self.object)
        
        messages.success(self.request, 'Account created successfully! Welcome to Finance Tracker.')
        return response

    def create_default_categories(self, user):
        """Create default income and expense categories for new users"""
        default_income_categories = [
            {'name': 'Salary', 'icon': '💼', 'color': '#10B981'},
            {'name': 'Freelance', 'icon': '💻', 'color': '#3B82F6'},
            {'name': 'Investment', 'icon': '📈', 'color': '#8B5CF6'},
            {'name': 'Gift', 'icon': '🎁', 'color': '#F59E0B'},
            {'name': 'Other Income', 'icon': '💰', 'color': '#06B6D4'},
        ]
        
        default_expense_categories = [
            {'name': 'Groceries', 'icon': '🛒', 'color': '#EF4444'},
            {'name': 'Transport', 'icon': '🚗', 'color': '#F97316'},
            {'name': 'Utilities', 'icon': '⚡', 'color': '#84CC16'},
            {'name': 'Entertainment', 'icon': '🎬', 'color': '#EC4899'},
            {'name': 'Healthcare', 'icon': '🏥', 'color': '#14B8A6'},
            {'name': 'Dining Out', 'icon': '🍽️', 'color': '#F59E0B'},
            {'name': 'Shopping', 'icon': '🛍️', 'color': '#8B5CF6'},
            {'name': 'Education', 'icon': '📚', 'color': '#3B82F6'},
            {'name': 'Insurance', 'icon': '🛡️', 'color': '#6B7280'},
            {'name': 'Other Expenses', 'icon': '💸', 'color': '#EF4444'},
        ]
        
        # Create income categories
        for cat_data in default_income_categories:
            Category.objects.create(
                user=user,
                name=cat_data['name'],
                category_type='income',
                icon=cat_data['icon'],
                color=cat_data['color']
            )
        
        # Create expense categories
        for cat_data in default_expense_categories:
            Category.objects.create(
                user=user,
                name=cat_data['name'],
                category_type='expense',
                icon=cat_data['icon'],
                color=cat_data['color']
            )


class ProfileView(LoginRequiredMixin, TemplateView):
    """User profile view"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = self.request.user.userprofile
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            context['profile'] = UserProfile.objects.create(user=self.request.user)
        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    """User settings view"""
    form_class = UserProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Settings updated successfully!')
        return super().form_valid(form)


class AccountListView(LoginRequiredMixin, ListView):
    """List user's accounts"""
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user).order_by('name')


class AccountCreateView(LoginRequiredMixin, CreateView):
    """Create new account"""
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Account "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class AccountUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing account"""
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Account "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class AccountDeleteView(LoginRequiredMixin, DeleteView):
    """Delete account"""
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('accounts:account_list')

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        account = self.get_object()
        messages.success(request, f'Account "{account.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CategoryListView(LoginRequiredMixin, ListView):
    """List user's categories"""
    model = Category
    template_name = 'accounts/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).order_by('category_type', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.get_queryset()
        context['income_categories'] = categories.filter(category_type='income')
        context['expense_categories'] = categories.filter(category_type='expense')
        return context


class CategoryCreateView(LoginRequiredMixin, CreateView):
    """Create new category"""
    model = Category
    form_class = CategoryForm
    template_name = 'accounts/category_form.html'
    success_url = reverse_lazy('accounts:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing category"""
    model = Category
    form_class = CategoryForm
    template_name = 'accounts/category_form.html'
    success_url = reverse_lazy('accounts:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    """Delete category"""
    model = Category
    template_name = 'accounts/category_confirm_delete.html'
    success_url = reverse_lazy('accounts:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        messages.success(request, f'Category "{category.name}" deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CustomLogoutView(View):
    """Custom logout view that accepts GET and POST requests"""
    
    def get(self, request):
        if request.user.is_authenticated:
            messages.success(request, f'You have been successfully logged out. Goodbye, {request.user.username}!')
        logout(request)
        return redirect('/')
    
    def post(self, request):
        if request.user.is_authenticated:
            messages.success(request, f'You have been successfully logged out. Goodbye, {request.user.username}!')
        logout(request)
        return redirect('/')
