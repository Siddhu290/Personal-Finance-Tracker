# Personal Finance Tracker

A comprehensive web-based personal finance management application built with Django and modern web technologies. Track your income, expenses, budgets, and financial goals with an intuitive and responsive interface.

![Finance Tracker Banner](https://via.placeholder.com/1200x400/3B82F6/ffffff?text=Personal+Finance+Tracker)

## 🌟 Features

### � **Dashboard & Analytics**
- Real-time financial overview with interactive charts
- Monthly and yearly financial summaries
- Net worth tracking across all accounts
- Customizable widgets and quick stats

### 💰 **Transaction Management**
- Add, edit, and categorize income and expenses
- Multi-account support (checking, savings, credit card, cash, investment)
- Transaction search and advanced filtering
- Receipt attachment support
- Bulk import/export (CSV, Excel)

### 🏷️ **Smart Categorization**
- Customizable income and expense categories
- Color-coded organization with custom icons
- Automatic categorization suggestions
- Tag-based transaction organization

### 📅 **Budget Planning**
- Category-based budget creation and tracking
- Visual progress indicators and alerts
- Budget vs. actual spending analysis
- Monthly budget rollover options

### 🔄 **Recurring Transactions**
- Automated recurring income and expenses
- Flexible scheduling (daily, weekly, monthly, yearly)
- Smart reminders and notifications
- One-click execution of due transactions

### 📈 **Financial Reports**
- Income vs. expense trend analysis
- Category spending breakdowns
- Monthly and yearly financial reports
- Account performance summaries
- Export reports to PDF/Excel

### 🎨 **Modern UI/UX**
- Responsive design for desktop and mobile
- Dark/light mode toggle
- Intuitive navigation and workflows
- Accessibility-focused design

### 🔒 **Security & Privacy**
- User authentication and authorization
- Secure password management
- Data encryption and protection
- Session management
- CSRF protection

### 📈 Reports & Analytics
- **Interactive Charts**: Pie charts, line graphs, and bar charts
- **Spending Trends**: Monthly and yearly spending analysis
- **Category Breakdown**: Detailed category-wise reports
- **Account Summaries**: Overview of all account balances

### 📱 Modern UI/UX
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Tailwind CSS**: Modern, clean, and customizable interface
- **Interactive Elements**: Smooth animations and transitions
- **Accessibility**: WCAG compliant design

## Technology Stack

- **Backend**: Django 4.2+
- **Frontend**: Tailwind CSS, Alpine.js
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Authentication**: Django's built-in auth system

## Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- PostgreSQL 12+ (recommended for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd personal-finance-tracker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL Database**
   
   **Option A: Automated Setup (Windows)**
   ```powershell
   # PowerShell
   .\setup_postgresql.ps1
   
   # Or Command Prompt
   setup_postgresql.bat
   ```
   
   **Option B: Manual Setup**
   
   First, install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
   
   Then create the database:
   ```sql
   -- Connect as postgres user
   psql -U postgres
   
   -- Create user and database
   CREATE USER finance_user WITH PASSWORD 'finance_password_2025';
   CREATE DATABASE finance_tracker_db OWNER finance_user;
   GRANT ALL PRIVILEGES ON DATABASE finance_tracker_db TO finance_user;
   ```
   
   **Option C: Use SQLite (Development Only)**
   
   If you prefer to use SQLite for development, update `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }
   ```

5. **Configure Environment Variables**
   
   Copy `.env.example` to `.env` and update with your settings:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your database credentials:
   ```env
   DATABASE_NAME=finance_tracker_db
   DATABASE_USER=finance_user
   DATABASE_PASSWORD=your_password_here
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

6. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

8. **Load Sample Data (optional)**
   ```bash
   python create_sample_data.py
   ```

9. **Run the development server**
   ```bash
   python manage.py runserver
   ```

10. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000`
   - Use demo credentials: **Username**: `demo`, **Password**: `demo123`
   - Or create a new account by clicking "Register"

## Demo Account

The application comes with a pre-configured demo account with sample data:

- **Username**: `demo`
- **Password**: `demo123`

The demo account includes:
- Sample accounts (checking, savings, credit card)
- Various income and expense categories
- Transaction history
- Budget allocations
- All features ready to explore

## Project Structure

```
personal-finance-tracker/
├── accounts/           # User authentication & account management
├── transactions/       # Transaction management
├── budgets/           # Budget planning & tracking
├── reports/           # Financial reports & analytics
├── templates/         # HTML templates
├── static/           # CSS, JS, images
├── finance_tracker/  # Main Django project
├── requirements.txt  # Python dependencies
└── manage.py        # Django management script
```

## Configuration

### Environment Variables
Create a `.env` file in the project root for production settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Currency Settings
- Default currency is USD
- Supported currencies: USD, EUR, GBP, JPY, CAD, AUD, CHF, CNY, INR
- Currency can be changed in user settings

## Key Features Detail

### Transaction Management
- **Add Transactions**: Quick transaction entry with auto-completion
- **Bulk Import**: Upload CSV/Excel files with transaction data
- **Recurring Transactions**: Set up monthly bills, subscriptions
- **Transfer Funds**: Move money between accounts
- **Search & Filter**: Find transactions by date, amount, category

### Budget System
- **Category Budgets**: Set monthly spending limits per category
- **Budget Tracking**: Real-time progress monitoring
- **Overspending Alerts**: Automatic notifications at 80% and 100%
- **Budget Analytics**: Historical budget performance

### Reporting
- **Dashboard Overview**: Quick snapshot of financial health
- **Income vs Expenses**: Monthly and yearly comparisons
- **Category Analysis**: Spending breakdown by category
- **Trends**: Identify spending patterns and trends
- **Account Balances**: Track account performance over time

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
The project follows Django best practices:
- Class-based views for better organization
- Model managers for complex queries
- Form validation and error handling
- Security best practices implemented

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Deployment

### Production Setup
1. Set environment variables
2. Configure database (PostgreSQL recommended)
3. Set up static file serving
4. Configure email settings for password reset
5. Use a production WSGI server (Gunicorn)

### Docker Support
A `Dockerfile` and `docker-compose.yml` can be added for containerized deployment.

## Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping enabled
- **Secure Headers**: Security middleware configured
- **User Data Isolation**: Each user can only access their own data

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue on GitHub or contact the development team.

## Screenshots

### Dashboard
![Dashboard](https://via.placeholder.com/600x400/3B82F6/FFFFFF?text=Dashboard+Overview)

### Transactions
![Transactions](https://via.placeholder.com/600x400/10B981/FFFFFF?text=Transaction+Management)

### Budgets
![Budgets](https://via.placeholder.com/600x400/F59E0B/FFFFFF?text=Budget+Tracking)

### Reports
![Reports](https://via.placeholder.com/600x400/8B5CF6/FFFFFF?text=Financial+Reports)

---

**Built with ❤️ using Django and Tailwind CSS**

## 🧪 Testing & Validation

The application has been thoroughly tested with:
- **Sample Data**: Pre-loaded demo data for immediate testing
- **Form Validation**: Client and server-side validation for all inputs
- **Chart Functionality**: Interactive charts with real-time data updates
- **Responsive Design**: Tested across different screen sizes and devices
- **Dark Mode**: Full dark mode support with proper contrast ratios
- **Browser Compatibility**: Tested on modern browsers (Chrome, Firefox, Safari, Edge)

### Demo Credentials
- **Username**: `demo`
- **Password**: `demo123`
- **Admin**: username `admin`, password `admin123`

## 🚀 Recent Enhancements

### Advanced Chart System
- Real-time chart updates with Chart.js
- Interactive income/expense trend analysis
- Category spending pie charts with drill-down capability
- Account balance visualization with historical trends

### Enhanced User Experience
- Quick action buttons for common tasks
- Real-time search and filtering
- Bulk transaction operations
- Smart form auto-completion and validation

### Improved Reports
- Dynamic chart data loading
- Advanced filtering and date range selection
- Export capabilities for all reports
- Mobile-optimized report viewing

### Performance Optimizations
- Efficient database queries with proper indexing
- Client-side caching for frequently accessed data
- Optimized JavaScript for smooth interactions
- Responsive image loading and chart rendering

## 📋 Project Status

✅ **Complete Features:**
- User authentication and profiles
- Account management (all types)
- Transaction CRUD operations
- Category management with customization
- Budget creation and tracking
- Recurring transaction system
- Comprehensive reporting dashboard
- Import/export functionality
- Dark/light mode theming
- Responsive mobile design
- Advanced search and filtering
- Interactive charts and analytics

🔄 **Ongoing Improvements:**
- Additional chart types and visualizations
- Enhanced mobile app experience
- Advanced budget forecasting
- Goal setting and tracking features
- Investment portfolio tracking
- Multi-currency support

## 🏗️ Architecture

Built with modern web development best practices:
- **Backend**: Django 5.2+ with class-based views
- **Frontend**: Tailwind CSS, Alpine.js, Chart.js
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Security**: CSRF protection, secure authentication, data validation
- **Performance**: Optimized queries, efficient JavaScript, responsive design
