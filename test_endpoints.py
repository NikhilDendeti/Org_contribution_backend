#!/usr/bin/env python3
"""Comprehensive endpoint testing script."""
import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:8001/api"

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.YELLOW}→ {text}{Colors.END}")

def test_endpoint(method, url, headers=None, data=None, files=None, description=""):
    """Test an endpoint and return response."""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        else:
            return None
        
        print_info(f"{method} {url}")
        if description:
            print(f"   {description}")
        
        if response.status_code in [200, 201]:
            print_success(f"Status: {response.status_code}")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)[:500]}...")
                return result
            except:
                print(f"   Response: {response.text[:200]}...")
                return response
        else:
            print_error(f"Status: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def main():
    print_header("Organization Contributions API - Endpoint Testing")
    
    tokens = {}
    raw_file_id = None
    
    # Step 1: Get tokens for all roles
    print_header("Step 1: Authentication - Getting Tokens")
    
    roles = {
        "CEO": "CEO001",
        "HOD": "HOD001",
        "Pod Lead": "PL001",
        "Employee": "EMP001"
    }
    
    for role_name, emp_code in roles.items():
        print(f"\n{Colors.BOLD}Testing {role_name} login ({emp_code}){Colors.END}")
        response = test_endpoint(
            "POST",
            f"{BASE_URL}/token/",
            data={"employee_code": emp_code},
            description=f"Get token for {role_name}"
        )
        if response and response.get("success"):
            tokens[role_name] = response["data"]["access"]
            print_success(f"{role_name} token obtained")
        else:
            print_error(f"Failed to get {role_name} token")
    
    if not tokens:
        print_error("Failed to get any tokens. Exiting.")
        return
    
    # Step 2: Seed products first
    print_header("Step 2: Seeding Products")
    print_info("Running seed_products command...")
    os.system("cd /home/nikhil/Projects/Org_contributions_backend && source venv/bin/activate && python manage.py seed_products")
    
    # Step 3: Upload Excel file
    print_header("Step 3: File Upload")
    
    # Try multiple possible paths for CSV or Excel files
    script_dir = Path(__file__).parent.absolute()
    base_dir = Path("/home/nikhil/Projects/Org_contributions_backend")
    
    # Try CSV first, then Excel
    possible_paths = [
        base_dir / "updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx",
        script_dir / "updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx",
        Path("updatedorganization_contributions_2025-10_all_sheets_normalized.xlsx"),
    ]
    
    excel_file = None
    for path in possible_paths:
        if path.exists():
            excel_file = path
            print_info(f"Found file at: {excel_file}")
            break
    
    if not excel_file:
        # Try to find any CSV or Excel file
        for path in [base_dir, script_dir]:
            csv_files = list(path.glob("*.csv"))
            if csv_files:
                excel_file = csv_files[0]
                print_info(f"Using found CSV file: {excel_file}")
                break
            xlsx_files = list(path.glob("*.xlsx"))
            if xlsx_files:
                excel_file = xlsx_files[0]
                print_info(f"Using found Excel file: {excel_file}")
                break
        
        if not excel_file:
            print_error(f"CSV/Excel file not found. Tried: {[str(p) for p in possible_paths]}")
            return
    
    print_info(f"Uploading file: {excel_file}")
    headers = {"Authorization": f"Bearer {tokens.get('HOD')}"}
    
    with open(excel_file, 'rb') as f:
        files = {'file': (excel_file.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = test_endpoint(
            "POST",
            f"{BASE_URL}/uploads/csv/",
            headers=headers,
            files=files,
            description="Upload Excel file (HOD role)"
        )
    
    if response and response.get("success"):
        raw_file_id = response["data"]["raw_file_id"]
        summary = response["data"]["summary"]
        print_success(f"File uploaded successfully!")
        print(f"   Raw File ID: {raw_file_id}")
        print(f"   Total Rows: {summary.get('total_rows', 0)}")
        print(f"   Created Records: {summary.get('created_records', 0)}")
        print(f"   Errors: {summary.get('error_count', 0)}")
    else:
        print_error("File upload failed")
        return
    
    # Step 4: Test Entity Endpoints
    print_header("Step 4: Entity Endpoints")
    
    # List Products
    headers = {"Authorization": f"Bearer {tokens.get('CEO')}"}
    products_response = test_endpoint(
        "GET",
        f"{BASE_URL}/products/",
        headers=headers,
        description="List all products"
    )
    
    if products_response and products_response.get("success"):
        products = products_response["data"]
        product_id = products[0]["id"] if products else None
        
        # List Features
        if product_id:
            test_endpoint(
                "GET",
                f"{BASE_URL}/features/?product_id={product_id}",
                headers=headers,
                description=f"List features for product {product_id}"
            )
    
    # Step 5: Test Upload Endpoints
    print_header("Step 5: Upload Management Endpoints")
    
    if raw_file_id:
        # Get upload details
        test_endpoint(
            "GET",
            f"{BASE_URL}/uploads/{raw_file_id}/",
            headers=headers,
            description="Get upload details"
        )
        
        # Download original file (just check if it works)
        print_info(f"GET {BASE_URL}/uploads/{raw_file_id}/download/")
        response = requests.get(
            f"{BASE_URL}/uploads/{raw_file_id}/download/",
            headers=headers
        )
        if response.status_code == 200:
            print_success(f"File download works (size: {len(response.content)} bytes)")
        else:
            print_error(f"File download failed: {response.status_code}")
        
        # Download errors CSV
        print_info(f"GET {BASE_URL}/uploads/{raw_file_id}/errors/")
        response = requests.get(
            f"{BASE_URL}/uploads/{raw_file_id}/errors/",
            headers=headers
        )
        if response.status_code == 200:
            print_success(f"Errors CSV download works (size: {len(response.content)} bytes)")
        else:
            print_info(f"Errors CSV: {response.status_code} (may have no errors)")
    
    # Step 6: Test Dashboard Endpoints
    print_header("Step 6: Dashboard Endpoints")
    
    month = "2025-10"
    
    # Organization Dashboard (CEO only)
    print(f"\n{Colors.BOLD}Testing Organization Dashboard (CEO role){Colors.END}")
    org_response = test_endpoint(
        "GET",
        f"{BASE_URL}/dashboards/org/?month={month}",
        headers={"Authorization": f"Bearer {tokens.get('CEO')}"},
        description="Get organization dashboard"
    )
    
    if org_response and org_response.get("success"):
        data = org_response["data"]
        print(f"   Total Hours: {data.get('total_hours', 0)}")
        print(f"   Products: {len(data.get('products', []))}")
    
    # Try with HOD (should fail)
    print(f"\n{Colors.BOLD}Testing Organization Dashboard with HOD (should fail){Colors.END}")
    test_endpoint(
        "GET",
        f"{BASE_URL}/dashboards/org/?month={month}",
        headers={"Authorization": f"Bearer {tokens.get('HOD')}"},
        description="Get organization dashboard (HOD - should be denied)"
    )
    
    # Department Dashboard (HOD)
    print(f"\n{Colors.BOLD}Testing Department Dashboard (HOD role){Colors.END}")
    # First, we need to get a department ID from the uploaded data
    # Let's try department ID 1 (Tech)
    dept_response = test_endpoint(
        "GET",
        f"{BASE_URL}/dashboards/department/1/?month={month}",
        headers={"Authorization": f"Bearer {tokens.get('HOD')}"},
        description="Get department dashboard"
    )
    
    if dept_response and dept_response.get("success"):
        data = dept_response["data"]
        print(f"   Department: {data.get('department_name', 'N/A')}")
        print(f"   Total Hours: {data.get('total_hours', 0)}")
        print(f"   Pods: {len(data.get('pods', []))}")
    
    # Pod Contributions (Pod Lead)
    print(f"\n{Colors.BOLD}Testing Pod Contributions (Pod Lead role){Colors.END}")
    # Try pod ID 1
    pod_response = test_endpoint(
        "GET",
        f"{BASE_URL}/pods/1/contributions/?month={month}",
        headers={"Authorization": f"Bearer {tokens.get('Pod Lead')}"},
        description="Get pod contributions"
    )
    
    if pod_response and pod_response.get("success"):
        data = pod_response["data"]
        print(f"   Pod: {data.get('pod_name', 'N/A')}")
        print(f"   Total Hours: {data.get('total_hours', 0)}")
        print(f"   Employees: {len(data.get('employees', []))}")
    
    # Employee Contributions
    print(f"\n{Colors.BOLD}Testing Employee Contributions{Colors.END}")
    # First, get the employee ID for EMP001 (should be 4 based on create_test_users)
    # Employees can only view their own contributions, so we need to use the correct employee_id
    # Let's try to get employee info or use employee_id=4 (EMP001)
    emp_response = test_endpoint(
        "GET",
        f"{BASE_URL}/employees/4/contributions/?month={month}",
        headers={"Authorization": f"Bearer {tokens.get('Employee')}"},
        description="Get employee contributions (EMP001 viewing own data)"
    )
    
    if emp_response and emp_response.get("success"):
        data = emp_response["data"]
        print(f"   Employee: {data.get('employee_name', 'N/A')} ({data.get('employee_code', 'N/A')})")
        print(f"   Total Hours: {data.get('total_hours', 0)}")
        print(f"   Products: {len(data.get('products', []))}")
        print(f"   Features: {len(data.get('features', []))}")
    
    # Step 7: Test Token Refresh
    print_header("Step 7: Token Refresh")
    
    # Get refresh tokens (we need to store them separately)
    refresh_tokens = {}
    for role, code in roles.items():
        token_response = requests.post(
            f"{BASE_URL}/token/",
            json={"employee_code": code},
            headers={"Content-Type": "application/json"}
        )
        if token_response.status_code == 200:
            token_data = token_response.json().get('data', {})
            refresh_tokens[role] = token_data.get('refresh')
    
    if refresh_tokens.get("CEO"):
        refresh_response = test_endpoint(
            "POST",
            f"{BASE_URL}/token/refresh/",
            data={"refresh": refresh_tokens.get("CEO")},
            description="Refresh CEO token"
        )
    
    # Summary
    print_header("Testing Summary")
    print_success("All endpoint tests completed!")
    print(f"\n{Colors.BOLD}Test Users:{Colors.END}")
    for role, code in roles.items():
        status = "✓" if tokens.get(role) else "✗"
        print(f"   {status} {role}: {code}")
    
    if raw_file_id:
        print(f"\n{Colors.BOLD}Uploaded File ID:{Colors.END} {raw_file_id}")
    
    print(f"\n{Colors.BOLD}Test Month:{Colors.END} {month}")

if __name__ == "__main__":
    main()

