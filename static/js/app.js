// Finance Tracker JavaScript utilities and enhancements

class FinanceTracker {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeCharts();
        this.setupFormEnhancements();
        this.setupSearchAndFilter();
        this.setupAccountBalance();
    }

    setupEventListeners() {
        // Auto-submit forms with data-auto-submit attribute
        document.querySelectorAll('form[data-auto-submit]').forEach(form => {
            form.addEventListener('change', (e) => {
                if (e.target.matches('select, input[type="checkbox"], input[type="radio"]')) {
                    form.submit();
                }
            });
        });

        // Confirm delete actions
        document.querySelectorAll('[data-confirm]').forEach(element => {
            element.addEventListener('click', (e) => {
                if (!confirm(element.dataset.confirm)) {
                    e.preventDefault();
                }
            });
        });

        // Copy to clipboard functionality
        document.querySelectorAll('[data-copy]').forEach(element => {
            element.addEventListener('click', () => {
                navigator.clipboard.writeText(element.dataset.copy);
                this.showToast('Copied to clipboard!', 'success');
            });
        });

        // Quick action buttons
        document.querySelectorAll('[data-quick-action]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.handleQuickAction(button.dataset.quickAction, button);
            });
        });
    }

    setupSearchAndFilter() {
        // Real-time search functionality
        const searchInputs = document.querySelectorAll('[data-search]');
        searchInputs.forEach(input => {
            let debounceTimer;
            input.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    this.performSearch(e.target.value, e.target.dataset.search);
                }, 300);
            });
        });

        // Advanced filter toggle
        const filterToggle = document.querySelector('[data-filter-toggle]');
        if (filterToggle) {
            filterToggle.addEventListener('click', () => {
                const filterPanel = document.querySelector('[data-filter-panel]');
                if (filterPanel) {
                    filterPanel.classList.toggle('hidden');
                }
            });
        }
    }

    setupAccountBalance() {
        // Real-time balance updates for transfers
        const fromAccountSelect = document.querySelector('#id_from_account');
        const toAccountSelect = document.querySelector('#id_to_account');
        const amountInput = document.querySelector('#id_amount');

        if (fromAccountSelect && toAccountSelect && amountInput) {
            [fromAccountSelect, toAccountSelect, amountInput].forEach(element => {
                element.addEventListener('change', () => {
                    this.updateTransferPreview();
                });
            });
        }
    }

    updateTransferPreview() {
        const fromAccount = document.querySelector('#id_from_account');
        const toAccount = document.querySelector('#id_to_account');
        const amount = document.querySelector('#id_amount');
        const preview = document.querySelector('[data-transfer-preview]');

        if (fromAccount && toAccount && amount && preview) {
            const fromValue = fromAccount.value;
            const toValue = toAccount.value;
            const amountValue = parseFloat(amount.value) || 0;

            if (fromValue && toValue && amountValue > 0) {
                const fromText = fromAccount.options[fromAccount.selectedIndex]?.text || '';
                const toText = toAccount.options[toAccount.selectedIndex]?.text || '';
                
                preview.innerHTML = `
                    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                        <h4 class="font-medium text-blue-900 dark:text-blue-200 mb-2">Transfer Preview</h4>
                        <p class="text-sm text-blue-800 dark:text-blue-300">
                            Transfer <strong>$${amountValue.toFixed(2)}</strong> from 
                            <strong>${fromText}</strong> to <strong>${toText}</strong>
                        </p>
                    </div>
                `;
                preview.classList.remove('hidden');
            } else {
                preview.classList.add('hidden');
            }
        }
    }

    performSearch(query, target) {
        const searchableElements = document.querySelectorAll(`[data-searchable="${target}"]`);
        
        searchableElements.forEach(element => {
            const text = element.textContent.toLowerCase();
            const matches = text.includes(query.toLowerCase());
            
            if (matches) {
                element.style.display = '';
                // Highlight matching text
                this.highlightText(element, query);
            } else {
                element.style.display = 'none';
            }
        });

        // Update results count
        const visibleCount = Array.from(searchableElements).filter(el => el.style.display !== 'none').length;
        const countElement = document.querySelector('[data-search-count]');
        if (countElement) {
            countElement.textContent = `${visibleCount} result${visibleCount !== 1 ? 's' : ''} found`;
        }
    }

    highlightText(element, query) {
        if (!query) return;
        
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        textNodes.forEach(textNode => {
            const text = textNode.textContent;
            const regex = new RegExp(`(${query})`, 'gi');
            if (regex.test(text)) {
                const highlightedText = text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-600">$1</mark>');
                const span = document.createElement('span');
                span.innerHTML = highlightedText;
                textNode.parentNode.replaceChild(span, textNode);
            }
        });
    }

    handleQuickAction(action, button) {
        switch (action) {
            case 'mark-paid':
                this.markTransactionPaid(button);
                break;
            case 'duplicate':
                this.duplicateTransaction(button);
                break;
            case 'toggle-recurring':
                this.toggleRecurring(button);
                break;
            default:
                console.log('Unknown quick action:', action);
        }
    }

    markTransactionPaid(button) {
        const transactionId = button.dataset.transactionId;
        if (transactionId) {
            // Show loading state
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            // Here you would make an AJAX call to mark as paid
            // For now, just simulate the action
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-check"></i> Paid';
                button.classList.remove('bg-yellow-500');
                button.classList.add('bg-green-500');
                this.showToast('Transaction marked as paid', 'success');
            }, 1000);
        }
    }

    duplicateTransaction(button) {
        const transactionId = button.dataset.transactionId;
        if (transactionId) {
            // Get transaction data and prefill form
            const transactionRow = button.closest('[data-transaction-id]');
            if (transactionRow) {
                this.showToast('Transaction duplicated! Edit the details and save.', 'info');
                // Here you would redirect to the transaction form with prefilled data
                window.location.href = `/transactions/add/?duplicate=${transactionId}`;
            }
        }
    }

    toggleRecurring(button) {
        const recurringId = button.dataset.recurringId;
        if (recurringId) {
            const isActive = button.classList.contains('bg-green-500');
            
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            // Simulate API call
            setTimeout(() => {
                if (isActive) {
                    button.innerHTML = '<i class="fas fa-pause"></i> Paused';
                    button.classList.remove('bg-green-500');
                    button.classList.add('bg-gray-500');
                    this.showToast('Recurring transaction paused', 'info');
                } else {
                    button.innerHTML = '<i class="fas fa-play"></i> Active';
                    button.classList.remove('bg-gray-500');
                    button.classList.add('bg-green-500');
                    this.showToast('Recurring transaction activated', 'success');
                }
                button.disabled = false;
            }, 1000);
        }
    }

    initializeCharts() {
        // Initialize pie charts
        document.querySelectorAll('.pie-chart').forEach(canvas => {
            this.createAdvancedPieChart(canvas);
        });

        // Initialize line charts
        document.querySelectorAll('.line-chart').forEach(canvas => {
            this.createAdvancedLineChart(canvas);
        });

        // Initialize bar charts
        document.querySelectorAll('.bar-chart').forEach(canvas => {
            this.createBarChart(canvas);
        });

        // Initialize income/expense charts specifically
        document.querySelectorAll('.income-expense-chart').forEach(canvas => {
            this.createAdvancedLineChart(canvas);
        });

        // Load dynamic chart data
        this.loadDynamicCharts();
    }

    createPieChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || this.getDefaultColors(data.labels?.length || 0),
                    borderWidth: 2,
                    borderColor: document.documentElement.classList.contains('dark') ? '#374151' : '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: $${value.toLocaleString()} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        this.charts[canvas.id] = chart;
    }

    createLineChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Income',
                    data: data.income || [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Expenses',
                    data: data.expenses || [],
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                        }
                    },
                    y: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280',
                            callback: (value) => '$' + value.toLocaleString()
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                        }
                    }
                }
            }
        });

        this.charts[canvas.id] = chart;
    }

    createBarChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        const chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Budgeted',
                    data: data.budgeted || [],
                    backgroundColor: '#3b82f6',
                    borderRadius: 4
                }, {
                    label: 'Spent',
                    data: data.spent || [],
                    backgroundColor: '#ef4444',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                        },
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280',
                            callback: (value) => '$' + value.toLocaleString()
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                        }
                    }
                }
            }
        });

        this.charts[canvas.id] = chart;
    }

    getDefaultColors(count) {
        const colors = [
            '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
            '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1'
        ];
        return colors.slice(0, count);
    }

    setupFormEnhancements() {
        // Auto-calculate remaining budget
        document.querySelectorAll('[data-budget-amount]').forEach(input => {
            input.addEventListener('input', this.updateBudgetCalculations);
        });

        // Auto-format currency inputs
        document.querySelectorAll('input[type="number"][step="0.01"]').forEach(input => {
            input.addEventListener('blur', (e) => {
                const value = parseFloat(e.target.value);
                if (!isNaN(value)) {
                    e.target.value = value.toFixed(2);
                }
            });
        });

        // Real-time form validation
        document.querySelectorAll('form[data-validate]').forEach(form => {
            form.addEventListener('input', (e) => {
                this.validateField(e.target);
            });
        });
    }

    updateBudgetCalculations() {
        // Implementation for budget calculations
        const form = this.closest('form');
        const amountInput = form.querySelector('[data-budget-amount]');
        const spentDisplay = form.querySelector('[data-spent-amount]');
        const remainingDisplay = form.querySelector('[data-remaining-amount]');
        
        if (amountInput && spentDisplay && remainingDisplay) {
            const budgeted = parseFloat(amountInput.value) || 0;
            const spent = parseFloat(spentDisplay.textContent.replace(/[^0-9.-]+/g, '')) || 0;
            const remaining = budgeted - spent;
            
            remainingDisplay.textContent = '$' + remaining.toFixed(2);
            remainingDisplay.className = remaining >= 0 ? 'text-green-600' : 'text-red-600';
        }
    }

    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';

        // Remove existing validation message
        const existingMessage = field.parentNode.querySelector('.validation-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Validate based on field type and attributes
        if (field.required && !value) {
            isValid = false;
            message = 'This field is required.';
        } else if (field.type === 'email' && value && !this.isValidEmail(value)) {
            isValid = false;
            message = 'Please enter a valid email address.';
        } else if (field.type === 'number' && value && isNaN(parseFloat(value))) {
            isValid = false;
            message = 'Please enter a valid number.';
        }

        // Update field styling and add message
        if (!isValid) {
            field.classList.add('border-red-500', 'focus:border-red-500');
            field.classList.remove('border-gray-300', 'focus:border-blue-500');
            
            const messageEl = document.createElement('p');
            messageEl.className = 'validation-message text-sm text-red-600 mt-1';
            messageEl.textContent = message;
            field.parentNode.appendChild(messageEl);
        } else {
            field.classList.remove('border-red-500', 'focus:border-red-500');
            field.classList.add('border-gray-300', 'focus:border-blue-500');
        }

        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-20 right-4 z-50 max-w-sm p-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-green-100 text-green-800 border border-green-200' :
            type === 'error' ? 'bg-red-100 text-red-800 border border-red-200' :
            type === 'warning' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
            'bg-blue-100 text-blue-800 border border-blue-200'
        }`;
        
        toast.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${
                    type === 'success' ? 'check-circle' :
                    type === 'error' ? 'exclamation-circle' :
                    type === 'warning' ? 'exclamation-triangle' :
                    'info-circle'
                } mr-2"></i>
                <span>${message}</span>
                <button class="ml-auto text-lg font-semibold" onclick="this.parentElement.parentElement.remove()">&times;</button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }
        }, 5000);
    }

    updateChartTheme() {
        Object.values(this.charts).forEach(chart => {
            const isDark = document.documentElement.classList.contains('dark');
            
            // Update chart colors for dark mode
            if (chart.options.plugins?.legend?.labels) {
                chart.options.plugins.legend.labels.color = isDark ? '#e5e7eb' : '#374151';
            }
            
            if (chart.options.scales) {
                Object.values(chart.options.scales).forEach(scale => {
                    if (scale.ticks) {
                        scale.ticks.color = isDark ? '#9ca3af' : '#6b7280';
                    }
                    if (scale.grid) {
                        scale.grid.color = isDark ? '#374151' : '#e5e7eb';
                    }
                });
            }
            
            chart.update();
        });
    }

    // Enhanced chart functionality
    async loadChartData(endpoint, chartId) {
        try {
            const response = await fetch(endpoint);
            const data = await response.json();
            this.updateChart(chartId, data);
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.showToast('Failed to load chart data', 'error');
        }
    }

    updateChart(chartId, newData) {
        const chart = this.charts[chartId];
        if (!chart) return;

        // Update chart data
        if (newData.data && Array.isArray(newData.data)) {
            chart.data.labels = newData.data.map(item => item.month || item.date || item.label);
            
            if (chart.config.type === 'line') {
                chart.data.datasets[0].data = newData.data.map(item => item.income || item.value);
                chart.data.datasets[1].data = newData.data.map(item => item.expenses || 0);
            } else if (chart.config.type === 'doughnut') {
                chart.data.datasets[0].data = newData.data.map(item => item.value || item.total);
                chart.data.datasets[0].backgroundColor = newData.colors || this.getDefaultColors(newData.data.length);
            }
        } else {
            // Handle other data formats
            if (newData.labels) chart.data.labels = newData.labels;
            if (newData.datasets) chart.data.datasets = newData.datasets;
        }

        chart.update('active');
    }

    createAdvancedLineChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(item => item.month_name),
                datasets: [{
                    label: 'Income',
                    data: data.map(item => item.income),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Expenses',
                    data: data.map(item => item.expenses),
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }, {
                    label: 'Net Income',
                    data: data.map(item => item.net),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: false,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151',
                            usePointStyle: true,
                            padding: 20
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                return `${context.dataset.label}: ${this.formatCurrency(context.parsed.y)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Month',
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                        },
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Amount ($)',
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280'
                        },
                        ticks: {
                            color: document.documentElement.classList.contains('dark') ? '#9ca3af' : '#6b7280',
                            callback: (value) => this.formatCurrency(value)
                        },
                        grid: {
                            color: document.documentElement.classList.contains('dark') ? '#374151' : '#e5e7eb'
                        }
                    }
                }
            }
        });

        this.charts[canvas.id] = chart;
    }

    createAdvancedPieChart(canvas) {
        const ctx = canvas.getContext('2d');
        const data = JSON.parse(canvas.dataset.chartData || '{}');
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.data || [],
                    backgroundColor: data.colors || this.getDefaultColors(data.labels?.length || 0),
                    borderWidth: 2,
                    borderColor: document.documentElement.classList.contains('dark') ? '#374151' : '#ffffff',
                    hoverBorderWidth: 4,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            color: document.documentElement.classList.contains('dark') ? '#e5e7eb' : '#374151',
                            generateLabels: (chart) => {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    const dataset = data.datasets[0];
                                    const total = dataset.data.reduce((a, b) => a + b, 0);
                                    
                                    return data.labels.map((label, i) => {
                                        const value = dataset.data[i];
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        return {
                                            text: `${label}: ${this.formatCurrency(value)} (${percentage}%)`,
                                            fillStyle: dataset.backgroundColor[i],
                                            strokeStyle: dataset.borderColor,
                                            lineWidth: dataset.borderWidth,
                                            hidden: isNaN(value),
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#ffffff',
                        bodyColor: '#ffffff',
                        borderColor: '#374151',
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${context.label}: ${this.formatCurrency(value)} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });

        this.charts[canvas.id] = chart;
    }

    loadDynamicCharts() {
        // Load income/expense chart data
        const incomeExpenseChart = document.querySelector('#income-expense-chart');
        if (incomeExpenseChart) {
            this.loadChartData('/reports/api/income-expense/', 'income-expense-chart');
        }

        // Load category pie chart data
        const categoryChart = document.querySelector('#category-chart');
        if (categoryChart) {
            this.loadChartData('/reports/api/category-pie/', 'category-chart');
        }

        // Load trends chart data
        const trendsChart = document.querySelector('#trends-chart');
        if (trendsChart) {
            this.loadChartData('/reports/api/trends/', 'trends-chart');
        }

        // Load account balance chart data
        const accountChart = document.querySelector('#account-balance-chart');
        if (accountChart) {
            this.loadChartData('/reports/api/account-balance/', 'account-balance-chart');
        }
    }

    // Real-time chart refresh functionality
    refreshCharts() {
        this.loadDynamicCharts();
        this.showToast('Charts updated', 'success');
    }

    // ...existing code...
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.financeTracker = new FinanceTracker();
    
    // Update charts when theme changes
    const observer = new MutationObserver(() => {
        window.financeTracker.updateChartTheme();
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['class']
    });
});

// Export for use in other scripts
window.FinanceTracker = FinanceTracker;
