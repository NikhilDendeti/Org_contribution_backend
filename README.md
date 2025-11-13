# Organization Contributions Backend

Django REST API backend for tracking monthly employee contributions across products (Academy, Intensive, NIAT).

## Features

- Excel/CSV file upload and parsing
- Role-based access control (CEO, HOD, Pod Lead, Employee, Admin)
- Organization-wide dashboards with percentage calculations
- Department, Pod, and Employee-level metrics
- JWT authentication
- Clean architecture pattern

## Setup

### Prerequisites

- Python 3.11+
- Virtual environment

### Installation

1. Clone the repository
2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser (optional):
```bash
python manage.py createsuperuser
```

6. Seed initial products:
```bash
python manage.py seed_products
```

7. Run development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication

- `POST /api/token/` - Get JWT tokens (requires `employee_code` in body)
- `POST /api/token/refresh/` - Refresh access token

### Uploads

- `POST /api/uploads/csv/` - Upload Excel/CSV file (requires authentication, HOD/Admin role)
- `GET /api/uploads/{id}/` - Get upload details
- `GET /api/uploads/{id}/download/` - Download original file
- `GET /api/uploads/{id}/errors/` - Download errors CSV

### Dashboards

- `GET /api/dashboards/org/?month=YYYY-MM` - Organization dashboard (CEO only)
- `GET /api/dashboards/department/{dept_id}/?month=YYYY-MM` - Department dashboard (HOD only)
- `GET /api/pods/{pod_id}/contributions/?month=YYYY-MM` - Pod contributions (Pod Lead/HOD)
- `GET /api/employees/{employee_id}/contributions/?month=YYYY-MM` - Employee contributions

### Entities

- `GET /api/products/` - List all products
- `GET /api/features/?product_id=X` - List features for a product

## Excel File Format

The system expects Excel files with the following columns:

- `employee_code` - Unique employee identifier
- `employee_name` - Employee name
- `email` - Employee email
- `department` - Department name
- `pod` - Pod/team name
- `product` - Product name (Academy, Intensive, NIAT)
- `feature_name` - Feature name (optional)
- `contribution_month` - Month in YYYY-MM format
- `effort_hours` - Hours worked (numeric)
- `description` - Description (optional)
- `reported_by` - Reporter email
- `source` - Source identifier

Multiple sheets are supported (each sheet typically represents a department).

## Load Default CSV Data

Instead of uploading files every time, you can load the default CSV file that's already in the project:

```bash
python manage.py load_default_csv
```

This will:
- Find the most recent CSV file in `media/uploads/`
- Load all contribution data from it
- Create employees, departments, pods, products, and features as needed

Options:
- `--file FILE`: Specify a specific CSV file (relative to media/uploads/)
- `--uploaded-by CODE`: Employee code of uploader (default: CEO001)
- `--force`: Force reload even if data already exists

Example:
```bash
# Load default CSV
python manage.py load_default_csv

# Load specific file
python manage.py load_default_csv --file 20251113_100953_675864_organization_contributions_2025-10.csv

# Force reload
python manage.py load_default_csv --force
```

## Management Commands

- `python manage.py seed_products` - Create initial products
- `python manage.py create_test_users` - Create test users for all roles
- `python manage.py generate_template` - Generate Excel template
- `python manage.py reparse_rawfile <id> [--delete-existing]` - Reparse a file

## API Documentation

Full OpenAPI 3.0 specification is available in `api_spec.yaml`. You can:

1. View it in Swagger UI: Import `api_spec.yaml` into [Swagger Editor](https://editor.swagger.io/)
2. Use it with API testing tools like Postman or Insomnia
3. Generate client SDKs using OpenAPI generators

### Quick API Examples

**Get Token:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "CEO001"}'
```

**Get Organization Dashboard:**
```bash
curl -X GET "http://localhost:8000/api/dashboards/org/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

**Upload File:**
```bash
curl -X POST http://localhost:8000/api/uploads/csv/ \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@organization_contributions_2025-10.xlsx"
```

## Percentage Calculation

Percentages are calculated using Decimal precision to avoid floating-point errors:
- All calculations use Decimal type
- Percentages rounded to 2 decimal places
- Sum validation ensures percentages total 100% (adjusts last item if rounding causes drift)

## Architecture

The project follows clean architecture pattern:

- **Views** (`views/`) - HTTP adapters
- **Interactors** (`interactors/`) - Business logic
- **Storages** (`storages/`) - Data access layer with DTOs
- **Presenters** (`presenters/`) - Response formatting
- **Services** (`services/`) - External services (JWT, file parsing, metrics)

## Environment Variables

Create a `.env` file (optional):

```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Database

Default: SQLite (development)
Production: PostgreSQL (configure in settings.py)

## Testing

Run tests:
```bash
python manage.py test
```

## License

Internal use only.

