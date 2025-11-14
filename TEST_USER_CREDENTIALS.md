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

#### PL006 - Platform Pod (Tech)
- **Employee Code:** `PL006`
- **Name:** Platform Pod Lead
- **Email:** platform_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Platform Pod
- **Department:** Tech
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL006"}'
```

#### PL007 - Infra Pod (Tech)
- **Employee Code:** `PL007`
- **Name:** Infra Pod Lead
- **Email:** infra_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Infra Pod
- **Department:** Tech
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL007"}'
```

#### PL008 - Mobile Pod (Tech)
- **Employee Code:** `PL008`
- **Name:** Mobile Pod Lead
- **Email:** mobile_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Mobile Pod
- **Department:** Tech
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL008"}'
```

#### PL009 - Backend Pod (Tech)
- **Employee Code:** `PL009`
- **Name:** Backend Pod Lead
- **Email:** backend_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Backend Pod
- **Department:** Tech
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL009"}'
```

#### PL010 - Growth Pod (Marketing)
- **Employee Code:** `PL010`
- **Name:** Growth Pod Lead
- **Email:** growth_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Growth
- **Department:** Marketing
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL010"}'
```

#### PL011 - Content Pod (Marketing)
- **Employee Code:** `PL011`
- **Name:** Content Pod Lead
- **Email:** content_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Content
- **Department:** Marketing
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL011"}'
```

#### PL012 - Field Sales Pod (Sales)
- **Employee Code:** `PL012`
- **Name:** Field Sales Pod Lead
- **Email:** field_sales_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Field Sales
- **Department:** Sales
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL012"}'
```

#### PL013 - Inside Sales Pod (Sales)
- **Employee Code:** `PL013`
- **Name:** Inside Sales Pod Lead
- **Email:** inside_sales_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Inside Sales
- **Department:** Sales
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL013"}'
```

#### PL014 - Payroll Pod (Finance)
- **Employee Code:** `PL014`
- **Name:** Payroll Pod Lead
- **Email:** payroll_pl@example.com
- **Role:** POD_LEAD
- **Pod:** Payroll
- **Department:** Finance
- **Access:** Own pod dashboard, pod members' contributions

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL014"}'
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

### 5. Automation User
- **Employee Code:** `AUTO001`
- **Name:** Automation User
- **Email:** automation@example.com
- **Role:** AUTOMATION
- **Access:** Upload initial XLSX files, generate Pod Lead allocation sheets
- **Use Case:** System automation for uploading initial contribution data and distributing sheets to Pod Leads

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "AUTO001"}'
```

**Key Endpoints:**
- `POST /api/automation/upload-initial-xlsx/` - Upload initial XLSX and generate Pod Lead sheets

---

### 6. Admin User
- **Employee Code:** `ADMIN001` (if created)
- **Name:** Admin User
- **Email:** admin@example.com
- **Role:** ADMIN
- **Access:** All administrative operations including:
  - Import employee master data
  - Upload feature CSVs
  - Generate Pod Lead sheets
  - Process allocations
  - Generate final master lists
  - Access all dashboards

**Login Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "ADMIN001"}'
```

**Note:** Admin user can be created using the management command:
```bash
python manage.py create_admin_user
```

---

## 📋 Quick Reference Table

| Role      | Employee Code | Password | Pod/Department | Access Level                    |
|-----------|---------------|----------|----------------|---------------------------------|
| CEO       | `CEO001`      | N/A      | -              | All dashboards, generate final master list |
| HOD       | `HOD001`      | N/A      | Tech           | Tech department dashboard        |
| HOD       | `HOD002`      | N/A      | Finance        | Finance department dashboard     |
| HOD       | `HOD003`      | N/A      | Sales          | Sales department dashboard       |
| HOD       | `HOD004`      | N/A      | Marketing      | Marketing department dashboard   |
| HOD       | `HOD005`      | N/A      | Business       | Business department dashboard    |
| Pod Lead  | `PL001`       | N/A      | Partnerships (Business) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL002`       | N/A      | Partnerships (Business) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL003`       | N/A      | Strategy (Business) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL004`       | N/A      | Accounts (Finance) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL005`       | N/A      | Accounts (Finance) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL006`       | N/A      | Platform Pod (Tech) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL007`       | N/A      | Infra Pod (Tech) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL008`       | N/A      | Mobile Pod (Tech) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL009`       | N/A      | Backend Pod (Tech) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL010`       | N/A      | Growth (Marketing) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL011`       | N/A      | Content (Marketing) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL012`       | N/A      | Field Sales (Sales) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL013`       | N/A      | Inside Sales (Sales) | Own Pod + Pod Members, submit allocations |
| Pod Lead  | `PL014`       | N/A      | Payroll (Finance) | Own Pod + Pod Members, submit allocations |
| Employee  | `EMP001`      | N/A      | Tech           | Own Contributions Only          |
| Automation| `AUTO001`     | N/A      | -              | Upload initial XLSX, generate sheets |
| Admin     | `ADMIN001`    | N/A      | -              | All administrative operations   |

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
- `role`: Employee role (CEO, HOD, POD_LEAD, EMPLOYEE, ADMIN, AUTOMATION)
- `department_id`: Department ID (null for CEO/Automation)
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

### Create Automation User
To create the automation user for Pod Lead allocation flow:
```bash
python manage.py create_automation_user
```

This creates:
- **Employee Code:** `AUTO001`
- **Name:** Automation User
- **Email:** automation@example.com
- **Role:** AUTOMATION

### Create Admin User
To create the admin user for administrative operations:
```bash
python manage.py create_admin_user
```

This creates:
- **Employee Code:** `ADMIN001`
- **Name:** Admin User
- **Email:** admin@example.com
- **Role:** ADMIN

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

---

## 🔄 Pod Lead Allocation Flow Users

### Automation User (AUTO001)
**Purpose:** Upload initial XLSX files and generate Pod Lead allocation sheets

**Workflow:**
1. Login with `AUTO001`
2. Upload initial XLSX file via `POST /api/automation/upload-initial-xlsx/`
3. System generates allocation sheets for all Pod Leads
4. Pod Leads receive sheets and fill percentages

**Example Usage:**
```bash
# Login
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "AUTO001"}'

# Upload initial XLSX (use the access token from above)
curl -X POST http://localhost:8001/api/automation/upload-initial-xlsx/ \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx" \
  -F "month=2025-10"
```

**Response Format:**
The response is organized by **department/sub-sheet teams** (Tech, Finance, Sales, Marketing, Business):
```json
{
  "success": true,
  "data": {
    "summary": {
      "generated_sheets": 3,
      "created_allocations": 0,
      "month": "2025-10",
      "total_employees": 36,
      "total_pods_in_file": 12,
      "pods_with_sheets": 3,
      "pods_skipped": 9,
      "teams_processed": 5
    },
    "teams": [
      {
        "department": "Business",
        "pods_with_sheets": 2,
        "pods_skipped": 0,
        "pods": [
          {
            "pod_id": 11,
            "pod_name": "Strategy",
            "pod_lead_code": "PL003",
            "sheet_path": "pod_lead_sheets/pod_11_allocation_2025-10.xlsx",
            "download_url": "/media/pod_lead_sheets/pod_11_allocation_2025-10.xlsx"
          },
          {
            "pod_id": 12,
            "pod_name": "Partnerships",
            "pod_lead_code": "PL001",
            "sheet_path": "pod_lead_sheets/pod_12_allocation_2025-10.xlsx",
            "download_url": "/media/pod_lead_sheets/pod_12_allocation_2025-10.xlsx"
          }
        ],
        "skipped_pods": []
      },
      {
        "department": "Finance",
        "pods_with_sheets": 1,
        "pods_skipped": 1,
        "pods": [
          {
            "pod_id": 5,
            "pod_name": "Accounts",
            "pod_lead_code": "PL004",
            "sheet_path": "pod_lead_sheets/pod_5_allocation_2025-10.xlsx",
            "download_url": "/media/pod_lead_sheets/pod_5_allocation_2025-10.xlsx"
          }
        ],
        "skipped_pods": [
          {
            "pod_name": "Payroll",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          }
        ]
      },
      {
        "department": "Tech",
        "pods_with_sheets": 0,
        "pods_skipped": 4,
        "pods": [],
        "skipped_pods": [
          {
            "pod_name": "Platform Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Infra Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Backend Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Mobile Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          }
        ]
      },
      {
        "department": "Marketing",
        "pods_with_sheets": 0,
        "pods_skipped": 2,
        "pods": [],
        "skipped_pods": [
          {
            "pod_name": "Content",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Growth",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          }
        ]
      },
      {
        "department": "Sales",
        "pods_with_sheets": 0,
        "pods_skipped": 2,
        "pods": [],
        "skipped_pods": [
          {
            "pod_name": "Field Sales",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Inside Sales",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          }
        ]
      }
    ],
    "errors": [],
    "has_errors": false
  },
  "message": "Initial XLSX uploaded and sheets generated successfully"
}
```

**Note:** The response is organized by **department/sub-sheet teams** (Tech, Finance, Sales, Marketing, Business), not by individual pods. Each team entry shows:
- `pods_with_sheets`: Number of pods in this department that have generated sheets
- `pods`: List of pods with sheets (including pod details and download URLs)
- `skipped_pods`: List of pods without Pod Leads (cannot generate sheets)

### Pod Leads (PL001-PL005)
**Additional Access:** Can now submit allocations for their pod members

**New Endpoints:**
- `GET /api/pod-leads/{pod_id}/allocation-sheet/?month=YYYY-MM` - Download allocation sheet
- `GET /api/pod-leads/{pod_id}/allocations/?month=YYYY-MM` - View current allocations
- `POST /api/pod-leads/{pod_id}/allocations/submit/` - Submit allocations with percentages

**Example Usage:**
```bash
# Login as Pod Lead
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL001"}'

# Download allocation sheet
curl -X GET "http://localhost:8001/api/pod-leads/12/allocation-sheet/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"

# Submit allocations
curl -X POST http://localhost:8001/api/pod-leads/12/allocations/submit/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "month": "2025-10",
    "allocations": [
      {
        "employee_id": 5,
        "product": "Academy",
        "product_description": "Feature X",
        "academy_percent": 40,
        "intensive_percent": 30,
        "niat_percent": 30,
        "is_verified_description": true
      }
    ]
  }'
```

### CEO/Admin Users
**Additional Access:** Can generate final master lists after all Pod Leads submit

**New Endpoints:**
- `POST /api/admin/final-master-list/generate/?month=YYYY-MM` - Generate final master list
- `GET /api/admin/final-master-list/?month=YYYY-MM` - Get final master list

**Example Usage:**
```bash
# Login as CEO/Admin
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "CEO001"}'

# Generate final master list
curl -X POST "http://localhost:8001/api/admin/final-master-list/generate/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

