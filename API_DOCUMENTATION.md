# API Documentation

Complete API reference for Organization Contributions Backend.

## Base URL

- Development: `http://localhost:8000/api`
- Production: `https://api.example.com/api`

## Authentication

All endpoints (except token generation) require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Test Users

| Role | Employee Code | Permissions |
|------|--------------|-------------|
| CEO | `CEO001` | Organization-wide dashboards |
| HOD | `HOD001` | Upload files, department dashboards |
| Pod Lead | `PL001` | Pod-level dashboards |
| Employee | `EMP001` | Own contribution data |

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

### 3. Dashboards

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
        "hours": 1500.00
      }
    ]
  }
}
```

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

### 4. Entities

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
- `AUTHENTICATION_FAILED` - Authentication failed (401)

## Rate Limiting

Currently no rate limiting is implemented. Consider adding rate limiting for production.

## Pagination

List endpoints support pagination:
- Default page size: 100
- Use `?page=1` query parameter

## Excel File Format

See README.md for detailed Excel file format specification.

## OpenAPI Specification

Full OpenAPI 3.0 specification available in `api_spec.yaml`. Import into Swagger UI or Postman for interactive documentation.

