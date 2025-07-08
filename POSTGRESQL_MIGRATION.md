# PostgreSQL Migration Guide

This guide walks you through migrating the Finance Tracker application from SQLite to PostgreSQL.

## Prerequisites

1. **PostgreSQL Installation**: Download and install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/windows/)
2. **Python Dependencies**: Ensure the following packages are installed:
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

## Quick Setup (Automated)

### Option 1: PowerShell Script (Recommended)
```powershell
.\setup_postgresql.ps1
```

### Option 2: Batch Script
```cmd
setup_postgresql.bat
```

## Manual Setup

If you prefer to set up PostgreSQL manually, follow these steps:

### 1. Create Database and User

Connect to PostgreSQL as superuser:
```bash
psql -U postgres
```

Run the following SQL commands:
```sql
-- Create user
CREATE USER finance_user WITH PASSWORD 'finance_password_2025';

-- Create database
CREATE DATABASE finance_tracker_db OWNER finance_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE finance_tracker_db TO finance_user;

-- Connect to the new database
\c finance_tracker_db;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO finance_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO finance_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO finance_user;

-- Exit psql
\q
```

## Environment Configuration

The application now uses environment variables for database configuration. The `.env` file contains:

```env
# Database Configuration
DATABASE_NAME=finance_tracker_db
DATABASE_USER=finance_user
DATABASE_PASSWORD=finance_password_2025
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Django Configuration  
SECRET_KEY=django-insecure-finance-tracker-2025-secret-key-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Important**: Never commit the `.env` file to version control. Use `.env.example` as a template.

## Django Migration

After setting up PostgreSQL, run the Django migrations:

```bash
# Apply migrations
python manage.py migrate

# Create a superuser (optional)
python manage.py createsuperuser

# Load sample data (optional)
python create_sample_data.py
```

## Configuration Details

### Database Settings

The `settings.py` file now uses environment variables:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DATABASE_NAME', 'finance_tracker_db'),
        'USER': os.getenv('DATABASE_USER', 'finance_user'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}
```

### Security Improvements

- Secret key is now loaded from environment variables
- Debug mode is controlled via environment variables
- Allowed hosts are configurable

## Troubleshooting

### Common Issues

1. **psycopg2 installation error**:
   ```bash
   pip install psycopg2-binary
   ```

2. **Connection refused**:
   - Ensure PostgreSQL service is running
   - Check if the port 5432 is correct
   - Verify firewall settings

3. **Authentication failed**:
   - Verify username and password in `.env`
   - Check PostgreSQL authentication method in `pg_hba.conf`

4. **Permission denied**:
   - Ensure the user has proper privileges on the database
   - Run the GRANT commands from the setup section

### PostgreSQL Service Management

**Windows (Services)**:
- Start: `net start postgresql-x64-15` (adjust version)
- Stop: `net stop postgresql-x64-15`

**Windows (PowerShell)**:
```powershell
# Check status
Get-Service -Name postgresql*

# Start service
Start-Service -Name "postgresql-x64-15"

# Stop service
Stop-Service -Name "postgresql-x64-15"
```

### Database Connection Test

Test the connection:
```bash
psql -h localhost -U finance_user -d finance_tracker_db
```

## Production Considerations

For production deployment:

1. **Environment Variables**: Use secure methods to manage environment variables
2. **Database Security**: 
   - Use strong passwords
   - Configure proper firewall rules
   - Enable SSL connections
3. **Backup Strategy**: Implement regular database backups
4. **Connection Pooling**: Consider using connection pooling for better performance

## Backup and Restore

### Backup
```bash
pg_dump -h localhost -U finance_user finance_tracker_db > backup.sql
```

### Restore
```bash
psql -h localhost -U finance_user finance_tracker_db < backup.sql
```

## Migration from SQLite (Data Transfer)

If you have existing SQLite data to migrate:

1. **Export data from SQLite**:
   ```bash
   python manage.py dumpdata --natural-foreign --natural-primary > data.json
   ```

2. **Switch to PostgreSQL** (follow this guide)

3. **Import data to PostgreSQL**:
   ```bash
   python manage.py loaddata data.json
   ```

## Next Steps

After successful PostgreSQL setup:

1. Test the application: `python manage.py runserver`
2. Verify all features work correctly
3. Update your deployment scripts
4. Consider setting up database monitoring
5. Implement backup procedures

For any issues, check the Django and PostgreSQL logs for detailed error messages.
