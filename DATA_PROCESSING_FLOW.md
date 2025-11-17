# Complete Data Processing Flow: Upload to Dashboard

## Overview
This document explains the complete flow from file upload to dashboard analytics generation.

---

## Step 1: File Upload (`POST /api/uploads/csv/`)

### What Happens:
1. **File Reception**
   - File is received via multipart/form-data
   - File is temporarily saved to disk

2. **Duplicate Check**
   - Calculates MD5 checksum of file content
   - Checks if file with same checksum already exists
   - Prevents duplicate uploads

3. **File Storage**
   - Saves file to `media/uploads/` directory
   - Creates `RawFile` record in database with:
     - File name, storage path, file size, checksum
     - Upload timestamp, uploaded_by (employee_id)

---

## Step 2: File Parsing (`file_parser_service.parse_excel_file()`)

### What Happens:
1. **File Type Detection**
   - Detects if file is Excel (.xlsx/.xls) or CSV
   - Handles multiple encodings for CSV (UTF-8, Latin-1, CP1252)

2. **Sheet Processing** (for Excel files)
   - Reads all sheets (skips "Master" sheet if exists)
   - Each sheet typically represents a department (Tech, Finance, Sales, etc.)

3. **Column Validation**
   - **Required columns:**
     - `employee_code`, `employee_name`, `email`
     - `department`, `pod`
     - `product`, `contribution_month`, `effort_hours`
   - **Optional columns:**
     - `feature_name`, `description`, `reported_by`, `source`

4. **Row Processing**
   - For each row in each sheet:
     - Normalizes column names (lowercase, trim whitespace)
     - Validates data (email format, month format, numeric hours)
     - Creates normalized row dictionary

5. **Output**
   - Returns: `(parsed_rows, errors)`
   - `parsed_rows`: List of validated row dictionaries
   - `errors`: List of validation errors (missing columns, invalid data, etc.)

---

## Step 3: Data Storage (`UploadContributionFileInteractor.execute()`)

### What Happens:
1. **Entity Creation/Retrieval** (in database transaction)
   For each parsed row:
   
   a. **Department**
      - `department_storage.get_or_create_department(row['department'])`
      - Creates department if doesn't exist (e.g., "Tech" → Department ID 1)
   
   b. **Pod**
      - `pod_storage.get_or_create_pod(row['pod'], dept.id)`
      - Creates pod if doesn't exist (e.g., "Platform Pod" → Pod ID 18)
      - Links pod to department
   
   c. **Product**
      - `product_storage.get_or_create_product(row['product'])`
      - Creates product if doesn't exist (e.g., "Academy" → Product ID 1)
   
   d. **Feature** (optional)
      - `feature_storage.get_or_create_feature(...)`
      - Only if `feature_name` is provided
   
   e. **Employee**
      - `employee_storage.get_or_create_employee(...)`
      - Creates employee if doesn't exist
      - Links employee to department and pod
      - Stores: employee_code, name, email

2. **ContributionRecord Creation**
   For each parsed row:
   ```python
   ContributionRecordDTO(
       employee_id=employee.id,
       department_id=dept.id,      # e.g., 1 (Tech)
       pod_id=pod.id,              # e.g., 18 (Platform Pod)
       product_id=product.id,       # e.g., 1 (Academy)
       feature_id=feature.id,      # Optional
       contribution_month=date(2025, 10, 1),  # Normalized to 1st of month
       effort_hours=Decimal('96.0'),
       description=row.get('description', ''),
       source_file_id=raw_file.id
   )
   ```

3. **Bulk Insert**
   - `contribution_storage.bulk_create_contributions(records, raw_file.id)`
   - Inserts all ContributionRecord entries into database in batches of 1000
   - Each record links to the RawFile that created it

### Database Tables Populated:
- `departments` - Department names
- `pods` - Pod/team names (linked to departments)
- `products` - Product names (Academy, Intensive, NIAT)
- `features` - Feature names (optional, linked to products)
- `employees` - Employee information
- `contribution_records` - **Main data table** with all contribution data

---

## Step 4: Dashboard Query (`GET /api/dashboards/department/1/?month=2025-10`)

### What Happens:

1. **Request Processing**
   - Validates HOD permission (employee must be HOD and department_id must match)
   - Parses month parameter: `"2025-10"` → `date(2025, 10, 1)`

2. **Metrics Calculation** (`calculate_department_metrics()`)

   a. **Total Hours for Department**
      ```sql
      SELECT SUM(effort_hours) 
      FROM contribution_records 
      WHERE department_id = 1 
        AND contribution_month = '2025-10-01'
      ```
      Result: `1600.0` hours

   b. **Pods Aggregation**
      ```sql
      SELECT pod_id, pod__name, SUM(effort_hours) as total_hours
      FROM contribution_records
      WHERE department_id = 1 
        AND contribution_month = '2025-10-01'
        AND pod_id IS NOT NULL
      GROUP BY pod_id, pod__name
      HAVING SUM(effort_hours) > 0
      ORDER BY total_hours DESC
      ```
      Results:
      - Pod 18 (Platform Pod): 400 hours
      - Pod 19 (Infra Pod): 400 hours
      - Pod 20 (Mobile Pod): 400 hours
      - Pod 21 (Backend Pod): 400 hours

   c. **Product Breakdown per Pod**
      For each pod (e.g., Pod 18):
      ```sql
      SELECT product_id, product__name, SUM(effort_hours) as hours
      FROM contribution_records
      WHERE department_id = 1 
        AND pod_id = 18
        AND contribution_month = '2025-10-01'
      GROUP BY product_id, product__name
      ORDER BY hours DESC
      ```
      Results for Platform Pod:
      - Product 2 (Intensive): 160 hours (40%)
      - Product 3 (NIAT): 144 hours (36%)
      - Product 1 (Academy): 96 hours (24%)

   d. **Department Product Distribution**
      ```sql
      SELECT product_id, product__name, SUM(effort_hours) as hours
      FROM contribution_records
      WHERE department_id = 1 
        AND contribution_month = '2025-10-01'
      GROUP BY product_id, product__name
      ORDER BY hours DESC
      ```
      Results:
      - Product 2 (Intensive): 640 hours (40%)
      - Product 3 (NIAT): 576 hours (36%)
      - Product 1 (Academy): 384 hours (24%)

3. **Percentage Calculation**
   - For each pod: `percent = (pod_hours / pod_total_hours) * 100`
   - For department: `percent = (product_hours / department_total_hours) * 100`
   - Rounded to 2 decimal places

4. **Response Assembly**
   - Combines all data into `DepartmentMetricsDTO`
   - Presents via `present_department_metrics()`
   - Returns JSON response

---

## Data Flow Summary

```
Excel File Upload
    ↓
File Saved to Disk
    ↓
Parse Excel File
    ├─ Read Sheets (Tech, Finance, Sales, etc.)
    ├─ Validate Columns
    └─ Parse Rows
    ↓
Create/Get Entities
    ├─ Departments (Tech, Finance, etc.)
    ├─ Pods (Platform Pod, Infra Pod, etc.)
    ├─ Products (Academy, Intensive, NIAT)
    ├─ Employees
    └─ Features (optional)
    ↓
Create ContributionRecords
    └─ Bulk Insert into Database
    ↓
Dashboard Query
    ├─ Filter by department_id + month
    ├─ Aggregate by pod_id
    ├─ Aggregate by product_id
    └─ Calculate percentages
    ↓
JSON Response
    └─ Department metrics with pods and products
```

---

## Key Points

1. **Data Source**: All dashboard data comes from `contribution_records` table
2. **Pods Shown**: Only pods that have ContributionRecord entries for that department and month
3. **Hours Calculation**: Sum of `effort_hours` from ContributionRecord entries
4. **Percentages**: Calculated relative to total hours (pod total or department total)
5. **No Duplicates**: Uses Django ORM aggregation with `.distinct()` and set tracking

---

## Example: How Your Response Was Generated

Your response shows:
- **4 pods** (Platform Pod, Infra Pod, Mobile Pod, Backend Pod)
- Each pod has **400 hours** total
- Each pod has same product distribution (40% Intensive, 36% NIAT, 24% Academy)

This means:
1. Your Excel file had rows for these 4 pods in the Tech department
2. Each pod had contribution records totaling 400 hours
3. Each pod's hours were distributed across products in the same ratio
4. The system aggregated and calculated percentages automatically





