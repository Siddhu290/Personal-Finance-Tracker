<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Finance Tracker Project Instructions

This is a comprehensive personal finance tracker web application built with Django and Tailwind CSS.

## Project Structure
- `accounts/` - User authentication, profiles, accounts, and categories management
- `transactions/` - Transaction management, transfers, recurring transactions
- `budgets/` - Budget planning, tracking, and alerts
- `reports/` - Financial reports, charts, and analytics
- `templates/` - HTML templates with Tailwind CSS styling
- `static/` - CSS, JavaScript, and other static assets

## Key Features
- User authentication with custom user profiles
- Multiple account types (checking, savings, credit card, cash, investment)
- Income/expense categorization with custom icons and colors
- Budget planning and tracking with progress indicators
- Recurring transactions and reminders
- Financial reports and charts using Chart.js
- Dark/light mode toggle
- Import/export transactions (CSV/Excel)
- Responsive design with Tailwind CSS

## Coding Guidelines
- Use Django best practices with class-based views
- Follow the existing model structure and relationships
- Use Tailwind CSS classes for styling
- Implement proper error handling and validation
- Add docstrings to all classes and methods
- Use Django's built-in security features
- Maintain consistent naming conventions

## Models Overview
- `UserProfile` - Extended user information
- `Account` - User's financial accounts
- `Category` - Income/expense categories
- `Transaction` - Individual financial transactions
- `RecurringTransaction` - Template for recurring transactions
- `Budget` - Monthly budget allocations
- `BudgetAlert` - Budget overspending notifications

## Frontend Technologies
- Tailwind CSS for styling
- Alpine.js for interactive components
- Chart.js for data visualization
- Font Awesome for icons
- Custom JavaScript utilities in `static/js/app.js`

## Development Notes
- Demo user credentials: username: `demo`, password: `demo123`
- Admin user credentials: username: `admin`, password: `admin123`
- The application includes sample data for testing
- All monetary values use Decimal for precision
- Dark mode preference is stored per user
