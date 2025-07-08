# Finance Tracker - Database Storage Guide

## 🗃️ Database Configuration

**Database Name:** `finance_tracker_db`  
**Database Type:** PostgreSQL  
**Host:** localhost:5432  
**User:** finance_user

## 📊 Main Data Tables

### 1. 👤 User Management
- **`auth_user`** - User accounts and authentication
  - Stores: username, password, email, first_name, last_name
  - This is Django's built-in user table

- **`accounts_userprofile`** - Extended user preferences
  - Stores: currency preference, dark_mode, email_notifications, budget_alerts
  - Links to: auth_user (one-to-one)

### 2. 💰 Financial Accounts
- **`accounts_account`** - Bank accounts, credit cards, cash
  - Stores: account name, type (checking/savings/credit_card/cash/investment), balance
  - Links to: auth_user (many accounts per user)

### 3. 🏷️ Categories
- **`accounts_category`** - Income and expense categories
  - Stores: category name, type (income/expense), color, icon
  - Links to: auth_user (many categories per user)

### 4. 💸 Transactions
- **`transactions_transaction`** - All financial transactions
  - Stores: amount, description, date, transaction_type (income/expense/transfer)
  - Links to: auth_user, accounts_account, accounts_category

- **`transactions_recurringtransaction`** - Recurring payment templates
  - Stores: amount, description, frequency (daily/weekly/monthly), start_date, next_due_date
  - Links to: auth_user, accounts_account, accounts_category

- **`transactions_transactionreminder`** - Bill reminders
  - Stores: reminder_date, is_sent
  - Links to: auth_user, transactions_recurringtransaction

### 5. 📊 Budget Management
- **`budgets_budget`** - Monthly budget allocations
  - Stores: budget amount, month, year
  - Links to: auth_user, accounts_category

- **`budgets_budgetalert`** - Budget overspending alerts
  - Stores: alert_type (warning/danger/critical), message, is_read
  - Links to: auth_user, budgets_budget

## 🔗 Data Relationships

```
User (auth_user)
├── UserProfile (accounts_userprofile) [1:1]
├── Accounts (accounts_account) [1:many]
│   └── Transactions (transactions_transaction) [1:many]
├── Categories (accounts_category) [1:many]
│   ├── Transactions (transactions_transaction) [1:many]
│   ├── RecurringTransactions (transactions_recurringtransaction) [1:many]
│   └── Budgets (budgets_budget) [1:many]
│       └── BudgetAlerts (budgets_budgetalert) [1:many]
└── TransactionReminders (transactions_transactionreminder) [1:many]
```

## 📈 Sample Data Structure

### Example User Data Flow:
1. **User Registration** → `auth_user` table
2. **Profile Setup** → `accounts_userprofile` table
3. **Add Bank Account** → `accounts_account` table
4. **Create Categories** → `accounts_category` table
5. **Record Transaction** → `transactions_transaction` table
6. **Set Budget** → `budgets_budget` table
7. **Budget Alert** → `budgets_budgetalert` table

### Example Record in `transactions_transaction`:
```sql
id: 1
user_id: 2
account_id: 5
category_id: 3
transaction_type: 'expense'
amount: 45.50
description: 'Grocery shopping at Walmart'
date: '2025-07-07'
created_at: '2025-07-07 14:30:00'
```

### Example Record in `accounts_account`:
```sql
id: 5
user_id: 2
name: 'Main Checking'
account_type: 'checking'
balance: 2500.75
is_active: true
created_at: '2025-01-15 10:00:00'
```

### Example Record in `budgets_budget`:
```sql
id: 12
user_id: 2
category_id: 3
amount: 400.00
month: 7
year: 2025
is_active: true
```

## 🔍 Key Data Points Stored

### Financial Data:
- ✅ Account balances (real-time)
- ✅ Transaction history (all income/expenses)
- ✅ Category-wise spending
- ✅ Budget allocations and tracking
- ✅ Recurring payment schedules

### User Preferences:
- ✅ Currency settings (USD, EUR, GBP, etc.)
- ✅ UI preferences (dark/light mode)
- ✅ Notification settings
- ✅ Account types and customizations

### Analytics Data:
- ✅ Monthly spending trends
- ✅ Budget vs actual comparisons
- ✅ Category-wise breakdowns
- ✅ Account performance metrics

## 🛡️ Data Security

- **User Isolation**: Each user can only access their own data
- **Password Security**: Django's built-in password hashing
- **CSRF Protection**: Built-in cross-site request forgery protection
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **Session Management**: Secure session handling

## 🔧 Database Administration

### Access the Database:
```bash
# Connect to PostgreSQL
psql -h localhost -U finance_user -d finance_tracker_db

# View all tables
\dt

# View specific table structure
\d transactions_transaction

# View table data
SELECT * FROM transactions_transaction LIMIT 10;
```

### Common Queries:
```sql
-- Get all transactions for a user
SELECT * FROM transactions_transaction WHERE user_id = 2;

-- Get account balances for a user
SELECT name, account_type, balance FROM accounts_account WHERE user_id = 2;

-- Get budget vs spending for current month
SELECT b.amount as budget, 
       COALESCE(SUM(t.amount), 0) as spent
FROM budgets_budget b
LEFT JOIN transactions_transaction t ON b.category_id = t.category_id
WHERE b.user_id = 2 AND b.month = 7 AND b.year = 2025
GROUP BY b.id, b.amount;
```

This database structure provides a comprehensive foundation for personal finance management with proper relationships, data integrity, and scalability.
