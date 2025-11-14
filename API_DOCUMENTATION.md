# API Documentation

Complete API reference for Organization Contributions Backend.

## Base URL

- Development: `http://localhost:8001/api` (or `http://localhost:8000/api` depending on your Django runserver port)
- Production: `https://api.example.com/api`

## Authentication

All endpoints (except token generation) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Test Users

| Role | Employee Code | Permissions |
|------|--------------|-------------|
| CEO | `CEO001` | Organization-wide dashboards, generate final master list |
| HOD | `HOD001` | Upload files, department dashboards |
| Pod Lead | `PL001` | Pod-level dashboards, submit allocations |
| Employee | `EMP001` | Own contribution data |
| Automation | `AUTO001` | Upload initial XLSX, generate Pod Lead sheets |
| Admin | `ADMIN001` | All administrative operations |

## Endpoints

### 1. Authentication

#### Get JWT Tokens
```http
POST /api/token/
Content-Type: application/json

{
  "employee_code": "CEO001"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Tokens generated successfully"
}
```

#### Refresh Token
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Token refreshed successfully"
}
```

**Note:** The JWT access token includes the following claims:
- `employee_id`: Employee database ID
- `employee_code`: Employee code (e.g., "HOD001")
- `role`: Employee role (CEO, HOD, POD_LEAD, EMPLOYEE, ADMIN, AUTOMATION)
- `department_id`: Department ID (null for CEO/Automation)
- `pod_id`: Pod ID (null if not assigned)

#### Get Current User Profile
```http
GET /api/me/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 2,
    "employee_code": "HOD001",
    "name": "Tech HOD",
    "email": "tech_hod@example.com",
    "role": "HOD",
    "department_id": 1,
    "department_name": "Tech",
    "pod_id": 13,
    "pod_name": "Tech Pod"
  }
}
```

**Use Case:** Frontend can use this endpoint to get the current user's `department_id` to automatically navigate to the correct department dashboard.

### 2. File Uploads

#### Upload Contribution File
```http
POST /api/uploads/csv/
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <Excel/CSV file>
```

**Required Role:** HOD, Admin, or CEO

**Response:**
```json
{
  "success": true,
  "data": {
    "raw_file_id": 1,
    "summary": {
      "total_rows": 100,
      "created_records": 95,
      "created_employees": 20,
      "created_departments": 3,
      "created_pods": 5,
      "created_products": 3,
      "created_features": 15,
      "error_count": 5
    },
    "errors": [
      {
        "sheet": "Tech",
        "row": 5,
        "field": "effort_hours",
        "message": "Invalid effort_hours: abc. Must be numeric"
      }
    ],
    "has_errors": true
  },
  "message": "File uploaded successfully"
}
```

#### Get Upload Details
```http
GET /api/uploads/{raw_file_id}/
Authorization: Bearer <token>
```

#### Download Original File
```http
GET /api/uploads/{raw_file_id}/download/
Authorization: Bearer <token>
```

#### Download Errors CSV
```http
GET /api/uploads/{raw_file_id}/errors/
Authorization: Bearer <token>
```

### 3. Pod Lead Allocation Flow

The Pod Lead allocation flow allows automation users to upload initial XLSX files, generate allocation sheets for Pod Leads, and process submissions into final master lists.

#### 3.1. Upload Initial XLSX (Automation User)

**Step 1:** Automation user uploads initial XLSX file with employee product data.

```http
POST /api/automation/upload-initial-xlsx/
Authorization: Bearer <automation_token>
Content-Type: multipart/form-data

file: <Excel file>
month: 2025-10
```

**Required Role:** AUTOMATION

**File Format:** The XLSX file should contain sheets with the following columns:
- `employee_code` - Employee code
- `employee_name` - Employee name
- `email` - Employee email
- `department` - Department name
- `pod` - Pod name
- `product` - Product name (Academy, Intensive, NIAT)
- `description` - Product description/feature
- `contribution_month` - Month in YYYY-MM format
- `effort_hours` - Hours worked (optional, for reference)

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "generated_sheets": 3,
      "created_allocations": 0,
      "month": "2025-11",
      "total_employees": 36,
      "total_pods_in_file": 12,
      "pods_with_sheets": 3,
      "pods_skipped": 9,
      "teams_processed": 5,
      "teams_with_sheets": 2
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
            "sheet_path": "pod_lead_sheets/pod_11_allocation_2025-11.xlsx",
            "download_url": "/api/pod-leads/11/allocation-sheet/download/?month=2025-11",
            "media_url": "/media/pod_lead_sheets/pod_11_allocation_2025-11.xlsx"
          },
          {
            "pod_id": 12,
            "pod_name": "Partnerships",
            "pod_lead_code": "PL001",
            "sheet_path": "pod_lead_sheets/pod_12_allocation_2025-11.xlsx",
            "download_url": "/api/pod-leads/12/allocation-sheet/download/?month=2025-11",
            "media_url": "/media/pod_lead_sheets/pod_12_allocation_2025-11.xlsx"
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
            "sheet_path": "pod_lead_sheets/pod_5_allocation_2025-11.xlsx",
            "download_url": "/api/pod-leads/5/allocation-sheet/download/?month=2025-11",
            "media_url": "/media/pod_lead_sheets/pod_5_allocation_2025-11.xlsx"
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
      },
      {
        "department": "Tech",
        "pods_with_sheets": 0,
        "pods_skipped": 4,
        "pods": [],
        "skipped_pods": [
          {
            "pod_name": "Backend Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Infra Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Mobile Pod",
            "employee_count": 3,
            "reason": "No Pod Lead assigned"
          },
          {
            "pod_name": "Platform Pod",
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

**What happens:**
1. System parses the XLSX file and extracts product/description data per employee
2. Creates `PodLeadAllocation` records (one per employee-product combination) with status `PENDING`
3. Generates allocation sheets for each pod with a Pod Lead
4. Returns download URLs for all generated sheets

#### 3.2. Get Pod Allocation Sheet (Pod Lead)

**Step 2:** Pod Lead downloads their allocation sheet.

**Option 1: Get Sheet Info**
```http
GET /api/pod-leads/{pod_id}/allocation-sheet/?month=2025-10
Authorization: Bearer <pod_lead_token>
```

**Required Role:** 
- POD_LEAD (for that specific pod)
- AUTOMATION (can access any pod's sheet)

**Response:**
```json
{
  "success": true,
  "data": {
    "pod_id": 1,
    "pod_name": "Platform Pod",
    "sheet_path": "pod_lead_sheets/pod_1_allocation_2025-10.xlsx",
    "download_url": "/api/pod-leads/1/allocation-sheet/download/?month=2025-10"
  },
  "message": "Sheet retrieved successfully"
}
```

**Option 2: Direct Download (Recommended)**
```http
GET /api/pod-leads/{pod_id}/allocation-sheet/download/?month=2025-10
Authorization: Bearer <pod_lead_token>
```

**Required Role:** 
- POD_LEAD (for that specific pod)
- AUTOMATION (can download any pod's sheet)

**Response:** Excel file download (binary stream)

**Note:** The `download_url` in the response already includes the `/api/` prefix. Use it directly:
- ✅ Correct: `http://0.0.0.0:8001/api/pod-leads/11/allocation-sheet/download/?month=2025-11`
- ❌ Wrong: `http://0.0.0.0:8001/api/api/pod-leads/11/allocation-sheet/download/?month=2025-11` (duplicate `/api/`)

**Sheet Format:** The downloaded Excel sheet contains:
- `employee_code` - Employee code
- `employee_name` - Employee name
- `email` - Employee email
- `department` - Department name
- `pod` - Pod name
- `product_description` - Product description (pre-filled from initial XLSX)
- `product` - Product name (pre-filled from initial XLSX)
- `contribution_month` - Month (pre-filled)
- `Academy_product_contribution` - Academy percentage (empty, for Pod Lead to fill)
- `Intensive_product_contribution` - Intensive percentage (empty, for Pod Lead to fill)
- `NIAT_product_contribution` - NIAT percentage (empty, for Pod Lead to fill)
- `is_verified_description` - Verification status (initially False)

**Note:** One row per employee-product combination.

#### 3.3. Get Pod Allocations (Pod Lead)

Pod Lead can view current allocation status for their pod.

```http
GET /api/pod-leads/{pod_id}/allocations/?month=2025-10
Authorization: Bearer <pod_lead_token>
```

**Required Role:** POD_LEAD (for that pod)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "employee_id": 5,
      "employee_code": "TE1000",
      "employee_name": "John Doe",
      "email": "john@example.com",
      "product": "Academy",
      "product_description": "Feature X",
      "academy_percent": 0.0,
      "intensive_percent": 0.0,
      "niat_percent": 0.0,
      "features_text": null,
      "is_verified_description": false,
      "baseline_hours": 160.0,
      "status": "PENDING",
      "total_percent": 0.0
    }
  ],
  "message": "Allocations retrieved successfully"
}
```

#### 3.4. Submit Pod Allocations (Pod Lead)

**Step 3:** Pod Lead fills percentages and verifies descriptions, then submits.

```http
POST /api/pod-leads/{pod_id}/allocations/submit/
Authorization: Bearer <pod_lead_token>
Content-Type: application/json

{
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
    },
    {
      "employee_id": 5,
      "product": "Intensive",
      "product_description": "Feature Y",
      "academy_percent": 0,
      "intensive_percent": 50,
      "niat_percent": 50,
      "is_verified_description": true
    }
  ]
}
```

**Required Role:** POD_LEAD (for that pod)

**Validation:**
- Percentages must sum to ≤ 100% for each allocation
- `product` field is required
- Allocation must exist (created from initial XLSX upload)
- Allocation must belong to this Pod Lead

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "updated_allocations": 2,
      "error_count": 0
    },
    "allocations": [
      {
        "id": 1,
        "employee_id": 5,
        "employee_code": "TE1000",
        "employee_name": "John Doe",
        "product": "Academy",
        "product_description": "Feature X",
        "academy_percent": 40.0,
        "intensive_percent": 30.0,
        "niat_percent": 30.0,
        "is_verified_description": true,
        "status": "SUBMITTED"
      }
    ],
    "errors": [],
    "has_errors": false
  },
  "message": "Allocations submitted successfully"
}
```

**What happens:**
1. System validates percentages (sum ≤ 100%)
2. Updates `PodLeadAllocation` records with percentages and verification status
3. Sets status based on verification:
   - If `is_verified_description = true` → status = `SUBMITTED`
   - If `is_verified_description = false` → status = `PENDING`
4. Returns updated allocations

**Status Logic:**
- **PENDING**: Allocation has percentages filled but description is not verified
- **SUBMITTED**: Allocation has percentages filled AND description is verified (`is_verified_description = true`)
- **PROCESSED**: Allocation has been processed into contribution records (by Admin)

#### 3.5. Process Pod Allocations (Admin)

**Step 4:** Admin processes submitted allocations to create contribution records.

```http
POST /api/admin/allocations/{pod_id}/process/?month=2025-10&output_format=records
Authorization: Bearer <admin_token>
```

**Required Role:** ADMIN or CEO

**Query Parameters:**
- `month` - Month in YYYY-MM format (required)
- `output_format` - Either `records` (default) or `csv` (optional)

**Response (output_format=records):**
```json
{
  "success": true,
  "data": {
    "processed_count": 10,
    "output_format": "records",
    "created_records": 30,
    "message": "Successfully processed 10 allocations into 30 contribution records"
  },
  "message": "Allocations processed successfully"
}
```

**What happens:**
- Converts percentages to hours: `hours = (percent / 100) * baseline_hours`
- Creates `ContributionRecord` entries for each product with non-zero percentage
- Sets allocation status to `PROCESSED`

#### 3.6. Generate Final Master List (Admin/CEO)

**Step 5:** After all Pod Leads have submitted, generate final master list.

```http
POST /api/admin/final-master-list/generate/?month=2025-10
Authorization: Bearer <admin_token>
```

**Required Role:** ADMIN or CEO

**Pre-condition:** All Pod Leads must have submitted (no PENDING allocations)

**Response:**
```json
{
  "success": true,
  "data": {
    "file_path": "final_master_lists/final_master_list_2025-10.xlsx",
    "download_url": "/media/final_master_lists/final_master_list_2025-10.xlsx",
    "month": "2025-10",
    "filename": "final_master_list_2025-10.xlsx"
  },
  "message": "Final master list generated successfully"
}
```

**Error Response (if pending allocations exist):**
```json
{
  "success": false,
  "data": {
    "error": "There are 5 pending allocations. All Pod Leads must submit before generating final master list.",
    "pending_count": 5
  },
  "message": "Pending allocations exist",
  "status_code": 400
}
```

**Master List Format:** The generated XLSX contains:
- Multiple sheets (one per department + Master sheet)
- Columns: `employee_code`, `employee_name`, `email`, `department`, `pod`, `product`, `description`, `contribution_month`, `effort_hours`
- One row per employee-product combination
- Hours calculated from percentages: `effort_hours = (percent / 100) * baseline_hours`

#### 3.7. Get Final Master List (Admin/CEO)

Retrieve an existing final master list.

```http
GET /api/admin/final-master-list/?month=2025-10
Authorization: Bearer <admin_token>
```

**Required Role:** ADMIN or CEO

**Response:**
```json
{
  "success": true,
  "data": {
    "file_path": "final_master_lists/final_master_list_2025-10.xlsx",
    "download_url": "/media/final_master_lists/final_master_list_2025-10.xlsx",
    "month": "2025-10",
    "filename": "final_master_list_2025-10.xlsx",
    "exists": true
  },
  "message": "Final master list found"
}
```

### 4. Dashboards

#### Organization Dashboard
```http
GET /api/dashboards/org/?month=2025-10
Authorization: Bearer <token>
```

**Required Role:** CEO

**Response:**
```json
{
  "success": true,
  "data": {
    "month": "2025-10",
    "total_hours": 5000.50,
    "products": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 2000.00,
        "percent": 40.00
      },
      {
        "product_id": 2,
        "product_name": "Intensive",
        "hours": 2000.00,
        "percent": 40.00
      },
      {
        "product_id": 3,
        "product_name": "NIAT",
        "hours": 1000.50,
        "percent": 20.00
      }
    ],
    "top_departments": [
      {
        "department_id": 1,
        "department_name": "Tech",
        "hours": 3000.00
      }
    ],
    "top_pods": [
      {
        "pod_id": 1,
        "pod_name": "Platform Pod",
        "department_id": 1,
        "department_name": "Tech",
        "hours": 4600.0,
        "percent": 8.33
      },
      {
        "pod_id": 2,
        "pod_name": "Infra Pod",
        "department_id": 1,
        "department_name": "Tech",
        "hours": 4600.0,
        "percent": 8.33
      },
      {
        "pod_id": 5,
        "pod_name": "Accounts",
        "department_id": 2,
        "department_name": "Finance",
        "hours": 4600.0,
        "percent": 8.33
      }
    ],
    "department_breakdown": [
      {
        "department_id": 1,
        "department_name": "Tech",
        "total_hours": 18400.0,
        "products": [
          {
            "product_id": 1,
            "product_name": "Academy",
            "hours": 4416.0,
            "percent": 24.0
          },
          {
            "product_id": 2,
            "product_name": "Intensive",
            "hours": 7360.0,
            "percent": 40.0
          },
          {
            "product_id": 3,
            "product_name": "NIAT",
            "hours": 6624.0,
            "percent": 36.0
          }
        ]
      },
      {
        "department_id": 2,
        "department_name": "Finance",
        "total_hours": 9200.0,
        "products": [
          {
            "product_id": 1,
            "product_name": "Academy",
            "hours": 2208.0,
            "percent": 24.0
          },
          {
            "product_id": 2,
            "product_name": "Intensive",
            "hours": 3680.0,
            "percent": 40.0
          },
          {
            "product_id": 3,
            "product_name": "NIAT",
            "hours": 3312.0,
            "percent": 36.0
          }
        ]
      }
    ]
  }
}
```

**Note:** The `department_breakdown` field provides hours by product across all departments, perfect for creating stacked bar charts showing product distribution per department.

#### Department Dashboard
```http
GET /api/dashboards/department/{dept_id}/?month=2025-10
Authorization: Bearer <token>
```

**Required Role:** HOD (for that department)

**Response:**
```json
{
  "success": true,
  "data": {
    "department_id": 1,
    "department_name": "Tech",
    "month": "2025-10",
    "total_hours": 3000.00,
    "pods": [
      {
        "pod_id": 1,
        "pod_name": "Platform Pod",
        "total_hours": 1500.00,
        "products": [
          {
            "product_id": 1,
            "product_name": "Academy",
            "hours": 750.00,
            "percent": 50.00
          }
        ]
      }
    ],
    "product_distribution": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 1500.00,
        "percent": 50.00
      }
    ]
  }
}
```

#### Pod Contributions
```http
GET /api/pods/{pod_id}/contributions/?month=2025-10
Authorization: Bearer <token>
```

**Required Role:** Pod Lead (for that pod) or HOD/CEO

**Response:**
```json
{
  "success": true,
  "data": {
    "pod_id": 1,
    "pod_name": "Platform Pod",
    "month": "2025-10",
    "total_hours": 1500.00,
    "products": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 750.00,
        "percent": 50.00
      }
    ],
    "employees": [
      {
        "employee_id": 1,
        "employee_code": "EMP001",
        "employee_name": "John Doe",
        "total_hours": 160.00,
        "products": [
          {
            "product_id": 1,
            "product_name": "Academy",
            "hours": 80.00,
            "percent": 50.00
          }
        ]
      }
    ]
  }
}
```

#### Employee Contributions
```http
GET /api/employees/{employee_id}/contributions/?month=2025-10
Authorization: Bearer <token>
```

**Required Role:** Employee (own data) or HOD/Pod Lead/CEO

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 1,
    "employee_code": "EMP001",
    "employee_name": "John Doe",
    "month": "2025-10",
    "total_hours": 160.00,
    "products": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 80.00,
        "percent": 50.00
      }
    ],
    "features": [
      {
        "feature_id": 1,
        "feature_name": "Content Review",
        "hours": 40.00,
        "percent": 25.00,
        "description": "Worked on Content Review for Academy"
      }
    ]
  }
}
```

### 5. Admin Operations

#### Import Employee Master Data

```http
POST /api/admin/employees/import/
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <CSV file>
```

**Required Role:** ADMIN

**CSV Format:**
- `employee_code` - Employee code
- `name` - Employee name
- `email` - Email address
- `dept` - Department name
- `pod` - Pod name
- `pod_head` - Pod Lead employee code (optional)

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "created_employees": 20,
      "updated_employees": 5,
      "created_departments": 2,
      "created_pods": 3
    }
  },
  "message": "Employee master data imported successfully"
}
```

#### Upload Feature CSV

```http
POST /api/admin/features/upload/
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <CSV file>
month: 2025-10
```

**Required Role:** ADMIN

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "generated_sheets": 5,
      "created_allocations": 30,
      "month": "2025-10"
    },
    "sheets": [...],
    "errors": [],
    "has_errors": false
  },
  "message": "Feature CSV uploaded and sheets generated successfully"
}
```

#### Generate All Pod Sheets

```http
POST /api/admin/sheets/generate-all/?month=2025-10
Authorization: Bearer <admin_token>
```

**Required Role:** ADMIN or CEO

**Query Parameters:**
- `month` - Month in YYYY-MM format (required, can also be in request body)

**Request Body (Optional):**
```json
{
  "month": "2025-10",
  "file_path": "/path/to/feature.csv"  // Optional: if provided, uploads features first
}
```

**Response (without file_path):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "generated_sheets": 5,
      "month": "2025-10"
    },
    "sheets": [
      {
        "pod_id": 1,
        "pod_name": "Platform Pod",
        "pod_lead_code": "PL001",
        "sheet_path": "pod_lead_sheets/pod_1_allocation_2025-10.xlsx",
        "download_url": "/media/pod_lead_sheets/pod_1_allocation_2025-10.xlsx"
      }
    ]
  },
  "message": "Sheets generated successfully for all pods"
}
```

**Response (with file_path):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "generated_sheets": 5,
      "created_allocations": 30,
      "month": "2025-10"
    },
    "sheets": [...],
    "errors": [],
    "has_errors": false
  },
  "message": "Sheets generated successfully for all pods"
}
```

**What happens:**
- If `file_path` is provided: Uploads feature CSV first, then generates sheets
- If `file_path` is not provided: Generates sheets from existing `PodLeadAllocation` records
- Only generates sheets for pods that have a Pod Lead assigned

### 6. Entities

#### List Products
```http
GET /api/products/
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Academy"
    },
    {
      "id": 2,
      "name": "Intensive"
    },
    {
      "id": 3,
      "name": "NIAT"
    }
  ]
}
```

#### List Features
```http
GET /api/features/?product_id=1
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Content Review",
      "product_id": 1,
      "product_name": "Academy",
      "description": "Content review feature"
    }
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

### Common Error Codes

- `NOT_FOUND` - Entity not found (404)
- `PERMISSION_DENIED` - Insufficient permissions (403)
- `VALIDATION_ERROR` - Validation failed (400)
- `INVALID_FILE_FORMAT` - Invalid file format (400)
- `DUPLICATE_UPLOAD` - File already uploaded (400)
- `DOMAIN_ERROR` - General domain error (400)
- `UPLOAD_ERROR` - File upload error (400)

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production.

## Pagination

**Note:** Pagination is currently not implemented. All list endpoints return complete results. Consider implementing pagination for production use if datasets become large.

## Complete Pod Lead Allocation Flow

### Overview

The Pod Lead allocation flow enables automated distribution of allocation sheets to Pod Leads, who then fill in percentage allocations for their team members across products.

### Flow Steps

1. **Automation User Uploads Initial XLSX**
   - Automation user (`AUTO001`) uploads XLSX file with employee product data
   - System parses file and creates `PodLeadAllocation` records (status: `PENDING`)
   - System generates allocation sheets for each pod with a Pod Lead
   - Sheets are available for download

2. **Pod Leads Download Sheets**
   - Pod Leads download their allocation sheet via API
   - Sheet contains pre-filled product descriptions and product names
   - Pod Leads fill in percentages for Academy, Intensive, and NIAT

3. **Pod Leads Submit Allocations**
   - Pod Leads submit allocations via API
   - System validates percentages (sum ≤ 100%)
   - Pod Leads verify descriptions (`is_verified_description = true`)
   - Status updated to `SUBMITTED`

4. **Admin Processes Allocations**
   - Admin processes submitted allocations
   - System converts percentages to hours: `hours = (percent / 100) * baseline_hours`
   - Creates `ContributionRecord` entries
   - Status updated to `PROCESSED`

5. **Generate Final Master List**
   - After all Pod Leads submit, Admin generates final master list
   - System checks no PENDING allocations exist
   - Generates XLSX with all teams/pods/employees
   - Multiple sheets (one per department + Master sheet)

6. **View Analytics**
   - Stakeholders use existing dashboard endpoints
   - Role-based access enforced
   - Metrics calculated from `ContributionRecord` entries

### Example Complete Flow

```bash
# Step 1: Automation user uploads initial XLSX
curl -X POST http://localhost:8001/api/automation/upload-initial-xlsx/ \
  -H "Authorization: Bearer <automation_token>" \
  -F "file=@initial_data.xlsx" \
  -F "month=2025-10"

# Step 2: Pod Lead downloads sheet
curl -X GET "http://localhost:8001/api/pod-leads/1/allocation-sheet/?month=2025-10" \
  -H "Authorization: Bearer <pod_lead_token>"

# Step 3: Pod Lead submits allocations
curl -X POST http://localhost:8001/api/pod-leads/1/allocations/submit/ \
  -H "Authorization: Bearer <pod_lead_token>" \
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

# Step 4: Admin processes allocations
curl -X POST "http://localhost:8001/api/admin/allocations/1/process/?month=2025-10" \
  -H "Authorization: Bearer <admin_token>"

# Step 5: Admin generates final master list
curl -X POST "http://localhost:8001/api/admin/final-master-list/generate/?month=2025-10" \
  -H "Authorization: Bearer <admin_token>"

# Step 6: View analytics (existing endpoints)
curl -X GET "http://localhost:8001/api/dashboards/org/?month=2025-10" \
  -H "Authorization: Bearer <ceo_token>"
```

## Excel File Format

### Initial XLSX Format (for Automation Upload)

The initial XLSX file should contain multiple sheets (one per department/team) with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| `employee_code` | Yes | Employee code (e.g., "TE1000") |
| `employee_name` | Yes | Employee name |
| `email` | Yes | Email address |
| `department` | Yes | Department name |
| `pod` | Yes | Pod name |
| `product` | Yes | Product name (Academy, Intensive, NIAT) |
| `description` | Yes | Product description/feature |
| `contribution_month` | Yes | Month in YYYY-MM format |
| `effort_hours` | No | Hours worked (for reference) |

**Note:** One row per employee-product combination. Multiple products for the same employee should be separate rows.

### Generated Pod Lead Sheet Format

The system generates sheets with the following columns:

| Column | Pre-filled | Description |
|--------|------------|-------------|
| `employee_code` | Yes | Employee code |
| `employee_name` | Yes | Employee name |
| `email` | Yes | Email address |
| `department` | Yes | Department name |
| `pod` | Yes | Pod name |
| `product_description` | Yes | Product description (from initial XLSX) |
| `product` | Yes | Product name (from initial XLSX) |
| `contribution_month` | Yes | Month |
| `Academy_product_contribution` | No | Academy percentage (Pod Lead fills) |
| `Intensive_product_contribution` | No | Intensive percentage (Pod Lead fills) |
| `NIAT_product_contribution` | No | NIAT percentage (Pod Lead fills) |
| `is_verified_description` | Yes | Verification status (initially False) |

**Note:** One row per employee-product combination.

### Final Master List Format

The final master list contains:

| Column | Description |
|--------|-------------|
| `employee_code` | Employee code |
| `employee_name` | Employee name |
| `email` | Email address |
| `department` | Department name |
| `pod` | Pod name |
| `product` | Product name |
| `description` | Product description |
| `contribution_month` | Month |
| `effort_hours` | Calculated hours from percentages |

**Note:** Multiple sheets (one per department + Master sheet).

## OpenAPI Specification

Full OpenAPI 3.0 specification available in `api_spec.yaml`. Import into Swagger UI or Postman for interactive documentation.

## Additional Notes

### Allocation Status Flow

- `PENDING` - Initial state after automation upload
- `SUBMITTED` - Pod Lead has filled and submitted percentages
- `PROCESSED` - Admin has processed into ContributionRecords

### Percentage Validation

- Sum of `academy_percent`, `intensive_percent`, and `niat_percent` must be ≤ 100%
- Each percentage must be ≥ 0
- Validation occurs during Pod Lead submission

### Baseline Hours

- Default baseline hours: 160 hours/month
- Can be configured per employee via `monthly_baseline_hours` field
- Used to calculate `effort_hours` from percentages: `hours = (percent / 100) * baseline_hours`

