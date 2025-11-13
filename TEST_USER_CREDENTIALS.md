# Test User Login Credentials

## 🔐 Login Credentials

All users login using their **Employee Code** (not email or password).

### Authentication Endpoint
```
POST http://localhost:8001/api/token/
Content-Type: application/json

Body:
{
  "employee_code": "<EMPLOYEE_CODE>"
}
```

---

## 👥 Test Users

### 1. CEO (Chief Executive Officer)
- **Employee Code:** `CEO001`
- **Name:** CEO User
- **Email:** ceo@example.com
- **Role:** CEO
- **Access:** Full access to all dashboards (org, department, pod, employee)

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "CEO001"}'
```

---

### 2. HOD (Head of Department)

Each department has its own HOD who can only access their department's dashboard.

#### HOD001 - Tech Department
- **Employee Code:** `HOD001`
- **Name:** Tech HOD
- **Email:** tech_hod@example.com
- **Role:** HOD
- **Department:** Tech (ID: 1)
- **Access:** Tech department dashboard only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD001"}'
```

#### HOD002 - Finance Department
- **Employee Code:** `HOD002`
- **Name:** Finance HOD
- **Email:** finance_hod@example.com
- **Role:** HOD
- **Department:** Finance (ID: 2)
- **Access:** Finance department dashboard only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD002"}'
```

#### HOD003 - Sales Department
- **Employee Code:** `HOD003`
- **Name:** Sales HOD
- **Email:** sales_hod@example.com
- **Role:** HOD
- **Department:** Sales (ID: 3)
- **Access:** Sales department dashboard only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD003"}'
```

#### HOD004 - Marketing Department
- **Employee Code:** `HOD004`
- **Name:** Marketing HOD
- **Email:** marketing_hod@example.com
- **Role:** HOD
- **Department:** Marketing (ID: 4)
- **Access:** Marketing department dashboard only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD004"}'
```

#### HOD005 - Business Department
- **Employee Code:** `HOD005`
- **Name:** Business HOD
- **Email:** business_hod@example.com
- **Role:** HOD
- **Department:** Business (ID: 5)
- **Access:** Business department dashboard only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD005"}'
```

---

### 3. Pod Lead

Each pod has its own Pod Lead who can access their pod's dashboard and pod members' data.

#### PL001 - Partnerships Pod
- **Employee Code:** `PL001`
- **Name:** Pod Lead 1
- **Email:** pl1@example.com
- **Role:** POD_LEAD
- **Pod:** Partnerships (ID: 12)
- **Department:** Business
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL001"}'
```

#### PL002 - Partnerships Pod
- **Employee Code:** `PL002`
- **Name:** Pod Lead 2
- **Email:** pl2@example.com
- **Role:** POD_LEAD
- **Pod:** Partnerships (ID: 12)
- **Department:** Business
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL002"}'
```

#### PL003 - Strategy Pod
- **Employee Code:** `PL003`
- **Name:** Pod Lead 3
- **Email:** pl3@example.com
- **Role:** POD_LEAD
- **Pod:** Strategy (ID: 11)
- **Department:** Business
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL003"}'
```

#### PL004 - Accounts Pod
- **Employee Code:** `PL004`
- **Name:** Pod Lead 4
- **Email:** pl4@example.com
- **Role:** POD_LEAD
- **Pod:** Accounts (ID: 5)
- **Department:** Finance
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL004"}'
```

#### PL005 - Accounts Pod
- **Employee Code:** `PL005`
- **Name:** Pod Lead 5
- **Email:** pl5@example.com
- **Role:** POD_LEAD
- **Pod:** Accounts (ID: 5)
- **Department:** Finance
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL005"}'
```

---

### 4. Employee
- **Employee Code:** `EMP001`
- **Name:** Employee User
- **Email:** employee@example.com
- **Role:** EMPLOYEE
- **Access:** Own contributions only

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "EMP001"}'
```

---

## 📋 Quick Reference Table

| Role      | Employee Code | Password | Pod/Department | Access Level                    |
|-----------|---------------|----------|----------------|---------------------------------|
| CEO       | `CEO001`      | N/A      | -              | All dashboards                  |
| HOD       | `HOD001`      | N/A      | Tech           | Tech department dashboard        |
| HOD       | `HOD002`      | N/A      | Finance        | Finance department dashboard     |
| HOD       | `HOD003`      | N/A      | Sales          | Sales department dashboard       |
| HOD       | `HOD004`      | N/A      | Marketing      | Marketing department dashboard   |
| HOD       | `HOD005`      | N/A      | Business       | Business department dashboard    |
| Pod Lead  | `PL001`       | N/A      | Partnerships   | Own Pod + Pod Members           |
| Pod Lead  | `PL002`       | N/A      | Partnerships   | Own Pod + Pod Members           |
| Pod Lead  | `PL003`       | N/A      | Strategy       | Own Pod + Pod Members           |
| Pod Lead  | `PL004`       | N/A      | Accounts       | Own Pod + Pod Members           |
| Pod Lead  | `PL005`       | N/A      | Accounts       | Own Pod + Pod Members           |
| Employee  | `EMP001`      | N/A      | Tech           | Own Contributions Only          |

**Note:** There is **NO password**. Authentication is done via Employee Code only.

---

## 🔑 Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Tokens generated successfully"
}
```

**JWT Token Claims:**
The access token includes the following claims (decode the JWT to access):
- `employee_id`: Employee database ID
- `employee_code`: Employee code (e.g., "HOD001")
- `role`: Employee role (CEO, HOD, POD_LEAD, EMPLOYEE, ADMIN)
- `department_id`: Department ID (null for CEO)
- `pod_id`: Pod ID (null if not assigned)

**Get User Profile:**
After login, you can get the current user's profile (including `department_id`) using:
```bash
GET /api/me/
Authorization: Bearer <access_token>
```

This is especially useful for HODs to automatically determine their department dashboard URL.

**Error Response (Invalid Code):**
```json
{
  "success": false,
  "message": "Employee not found",
  "error_code": "ENTITY_NOT_FOUND"
}
```

---

## 📝 Usage Example

### JavaScript/Fetch
```javascript
const response = await fetch('http://localhost:8001/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    employee_code: 'CEO001'
  })
});

const data = await response.json();
const accessToken = data.data.access;

// Use token in subsequent requests
fetch('http://localhost:8001/api/dashboards/org/?month=2025-10', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

### Python/Requests
```python
import requests

# Login
response = requests.post(
    'http://localhost:8001/api/token/',
    json={'employee_code': 'CEO001'}
)

data = response.json()
access_token = data['data']['access']

# Use token
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(
    'http://localhost:8001/api/dashboards/org/?month=2025-10',
    headers=headers
)
```

---

## 🚀 Setup Commands

### Create Test Users
If users don't exist, create them with:
```bash
python manage.py create_test_users
```

This creates all test users automatically (CEO, HODs, Pod Leads, Employee).

### Load Default CSV Data
Instead of uploading files every time, load the default CSV file:
```bash
python manage.py load_default_csv
```

This will:
- Find the most recent CSV file in `media/uploads/`
- Load all contribution data automatically
- Create employees, departments, pods, products, and features

Options:
- `--file FILE`: Specify a specific CSV file
- `--uploaded-by CODE`: Employee code of uploader (default: CEO001)
- `--force`: Force reload even if data exists

Example:
```bash
# Load default CSV
python manage.py load_default_csv

# Force reload
python manage.py load_default_csv --force
```

