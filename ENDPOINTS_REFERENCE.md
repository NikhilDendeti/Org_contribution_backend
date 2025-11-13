# API Endpoints Reference

Complete list of all API endpoints with request/response examples.

## Base URL
```
http://localhost:8001/api
```

---

## 🔐 Authentication Endpoints

### 1. Login (Get JWT Tokens)

**Endpoint:** `POST /api/token/`

**Request:**
```bash
curl -X POST http://localhost:8001/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD001"}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzMDM1MTk4LCJpYXQiOjE3NjMwMzE1OTgsImp0aSI6IjBjOTU0YjdjZjllZTQ4MDBiMGFlNjlmb2E4YTZhOTczIiwiZW1wbG95ZWVfaWQiOjIsImVtcGxveWVlX2NvZGUiOiJIT0QwMDEiLCJyb2xlIjoiSE9EIiwiZGVwYXJ0bWVudF9pZCI6MSwicG9kX2lkIjoxM30...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2MzExNzk5OCwiaWF0IjoxNzYzMDMxNTk4LCJqdGkiOiIwYzk1NGI3Y2Y5ZWU0ODAwYjBhZTY5Zm9hOGE2YTk3MyIsImVtcGxveWVlX2lkIjoyLCJlbXBsb3llZV9jb2RlIjoiSE9EMDAxIiwicm9sZSI6IkhPRCIsImRlcGFydG1lbnRfaWQiOjEsInBvZF9pZCI6MTN9..."
  },
  "message": "Tokens generated successfully"
}
```

**JWT Token Payload (Decoded):**
```json
{
  "token_type": "access",
  "exp": 1763035198,
  "iat": 1763031598,
  "jti": "0c954b7cf9ee4800b0ae69f88a3a6973",
  "employee_id": 2,
  "employee_code": "HOD001",
  "role": "HOD",
  "department_id": 1,
  "pod_id": 13
}
```

---

### 2. Refresh Token

**Endpoint:** `POST /api/token/refresh/`

**Request:**
```bash
curl -X POST http://localhost:8001/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "message": "Token refreshed successfully"
}
```

---

### 3. Get Current User Profile

**Endpoint:** `GET /api/me/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/me/ \
  -H "Authorization: Bearer <access_token>"
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

**Use Case:** Frontend can use this to get `department_id` and automatically navigate to the correct dashboard.

---

## 📤 Upload Endpoints

### 4. Upload Contribution File

**Endpoint:** `POST /api/uploads/csv/`

**Request:**
```bash
curl -X POST http://localhost:8001/api/uploads/csv/ \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@organization_contributions_2025-10.csv"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "raw_file_id": 1,
    "summary": {
      "total_rows": 80,
      "created_records": 75,
      "created_employees": 15,
      "created_departments": 5,
      "created_pods": 8,
      "created_products": 3,
      "created_features": 12,
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
  "message": "File uploaded and processed successfully"
}
```

**Required Role:** HOD, Admin, or CEO

---

### 5. Get Raw File Details

**Endpoint:** `GET /api/uploads/<raw_file_id>/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/uploads/1/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "file_name": "organization_contributions_2025-10.csv",
    "file_path": "/media/uploads/20251113_100953_675864_organization_contributions_2025-10.csv",
    "uploaded_at": "2025-11-13T10:09:53Z",
    "uploaded_by": "HOD001",
    "summary": {
      "total_rows": 80,
      "created_records": 75,
      "error_count": 5
    },
    "has_errors": true
  }
}
```

---

### 6. Download Raw File

**Endpoint:** `GET /api/uploads/<raw_file_id>/download/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/uploads/1/download/ \
  -H "Authorization: Bearer <access_token>" \
  -o downloaded_file.csv
```

**Response:** File download (binary)

---

### 7. Download Errors CSV

**Endpoint:** `GET /api/uploads/<raw_file_id>/errors/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/uploads/1/errors/ \
  -H "Authorization: Bearer <access_token>" \
  -o errors.csv
```

**Response:** CSV file with error details (binary)

---

## 📊 Dashboard Endpoints

### 8. Organization Dashboard (CEO Only)

**Endpoint:** `GET /api/dashboards/org/?month=YYYY-MM`

**Request:**
```bash
curl -X GET "http://localhost:8001/api/dashboards/org/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "month": "2025-10",
    "total_hours": 1500.0,
    "product_breakdown": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 600.0,
        "percentage": 40.0
      },
      {
        "product_id": 2,
        "product_name": "Intensive",
        "hours": 500.0,
        "percentage": 33.33
      },
      {
        "product_id": 3,
        "product_name": "NIAT",
        "hours": 400.0,
        "percentage": 26.67
      }
    ],
    "top_contributing_teams": [
      {
        "department_id": 1,
        "department_name": "Tech",
        "hours": 800.0,
        "percentage": 53.33
      },
      {
        "department_id": 2,
        "department_name": "Finance",
        "hours": 700.0,
        "percentage": 46.67
      }
    ],
    "department_breakdown": [
      {
        "department_id": 1,
        "department_name": "Tech",
        "hours": 800.0,
        "percentage": 53.33,
        "pods": [
          {
            "pod_id": 1,
            "pod_name": "Tech Pod",
            "hours": 800.0
          }
        ]
      }
    ]
  }
}
```

**Required Role:** CEO

---

### 9. Department Dashboard (HOD)

**Endpoint:** `GET /api/dashboards/department/<dept_id>/?month=YYYY-MM`

**Request:**
```bash
curl -X GET "http://localhost:8001/api/dashboards/department/1/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "department_id": 1,
    "department_name": "Tech",
    "month": "2025-10",
    "total_hours": 800.0,
    "product_breakdown": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 400.0,
        "percentage": 50.0
      },
      {
        "product_id": 2,
        "product_name": "Intensive",
        "hours": 300.0,
        "percentage": 37.5
      },
      {
        "product_id": 3,
        "product_name": "NIAT",
        "hours": 100.0,
        "percentage": 12.5
      }
    ],
    "pod_breakdown": [
      {
        "pod_id": 1,
        "pod_name": "Tech Pod",
        "hours": 800.0,
        "percentage": 100.0,
        "employees": [
          {
            "employee_id": 4,
            "employee_code": "EMP001",
            "employee_name": "Employee User",
            "hours": 200.0,
            "percentage": 25.0
          }
        ]
      }
    ],
    "top_contributing_employees": [
      {
        "employee_id": 4,
        "employee_code": "EMP001",
        "employee_name": "Employee User",
        "hours": 200.0,
        "percentage": 25.0
      }
    ]
  }
}
```

**Required Role:** HOD (for their own department) or CEO

---

### 10. Pod Contributions

**Endpoint:** `GET /api/pods/<pod_id>/contributions/?month=YYYY-MM`

**Request:**
```bash
curl -X GET "http://localhost:8001/api/pods/1/contributions/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pod_id": 1,
    "pod_name": "Tech Pod",
    "month": "2025-10",
    "total_hours": 800.0,
    "product_breakdown": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 400.0,
        "percentage": 50.0
      }
    ],
    "employee_breakdown": [
      {
        "employee_id": 4,
        "employee_code": "EMP001",
        "employee_name": "Employee User",
        "hours": 200.0,
        "percentage": 25.0,
        "contributions": [
          {
            "product_id": 1,
            "product_name": "Academy",
            "feature_id": 1,
            "feature_name": "Feature 1",
            "hours": 200.0,
            "percentage": 100.0
          }
        ]
      }
    ]
  }
}
```

**Required Role:** Pod Lead (for their own pod), HOD (for pods in their department), or CEO

---

### 11. Employee Contributions

**Endpoint:** `GET /api/employees/<employee_id>/contributions/?month=YYYY-MM`

**Request:**
```bash
curl -X GET "http://localhost:8001/api/employees/4/contributions/?month=2025-10" \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "employee_id": 4,
    "employee_code": "EMP001",
    "employee_name": "Employee User",
    "month": "2025-10",
    "total_hours": 200.0,
    "contributions": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "feature_id": 1,
        "feature_name": "Feature 1",
        "hours": 200.0,
        "percentage": 100.0
      }
    ],
    "product_summary": [
      {
        "product_id": 1,
        "product_name": "Academy",
        "hours": 200.0,
        "percentage": 100.0
      }
    ]
  }
}
```

**Required Role:** Employee (for their own data), Pod Lead (for pod members), HOD (for department employees), or CEO

---

## 📋 Entity Endpoints

### 12. List Products

**Endpoint:** `GET /api/products/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/products/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Academy",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "Intensive",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": 3,
      "name": "NIAT",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 13. List Features

**Endpoint:** `GET /api/features/`

**Request:**
```bash
curl -X GET http://localhost:8001/api/features/ \
  -H "Authorization: Bearer <access_token>"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Feature 1",
      "product_id": 1,
      "product_name": "Academy",
      "description": "Feature description",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

## 🔑 Authentication Header

All endpoints (except `/api/token/` and `/api/token/refresh/`) require authentication:

```
Authorization: Bearer <access_token>
```

---

## 📝 Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Success"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "error_code": "ERROR_CODE"
}
```

### Validation Error Response
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "field_name": ["Error message"]
  }
}
```

---

## 🚨 Error Codes

- `ENTITY_NOT_FOUND`: Resource not found
- `PERMISSION_DENIED`: User doesn't have permission
- `VALIDATION_ERROR`: Invalid input data
- `INVALID_FILE_FORMAT`: File format not supported
- `DUPLICATE_UPLOAD`: File already uploaded
- `DOMAIN_ERROR`: General domain error

---

## 📌 Quick Reference

| Endpoint | Method | Auth Required | Role Required |
|----------|--------|---------------|---------------|
| `/api/token/` | POST | No | - |
| `/api/token/refresh/` | POST | No | - |
| `/api/me/` | GET | Yes | Any |
| `/api/uploads/csv/` | POST | Yes | HOD/Admin/CEO |
| `/api/uploads/<id>/` | GET | Yes | Any |
| `/api/uploads/<id>/download/` | GET | Yes | Any |
| `/api/uploads/<id>/errors/` | GET | Yes | Any |
| `/api/dashboards/org/` | GET | Yes | CEO |
| `/api/dashboards/department/<id>/` | GET | Yes | HOD (own dept)/CEO |
| `/api/pods/<id>/contributions/` | GET | Yes | Pod Lead/HOD/CEO |
| `/api/employees/<id>/contributions/` | GET | Yes | Employee (own)/Pod Lead/HOD/CEO |
| `/api/products/` | GET | Yes | Any |
| `/api/features/` | GET | Yes | Any |

---

## 💡 Frontend Integration Example

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8001/api/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ employee_code: 'HOD001' })
});
const { data: { access } } = await loginResponse.json();

// 2. Get user profile to determine department_id
const profileResponse = await fetch('http://localhost:8001/api/me/', {
  headers: { 'Authorization': `Bearer ${access}` }
});
const { data: { department_id } } = await profileResponse.json();

// 3. Navigate to department dashboard
const dashboardResponse = await fetch(
  `http://localhost:8001/api/dashboards/department/${department_id}/?month=2025-10`,
  { headers: { 'Authorization': `Bearer ${access}` } }
);
const dashboardData = await dashboardResponse.json();
```

---

**Last Updated:** 2025-11-13

