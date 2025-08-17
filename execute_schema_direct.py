#!/usr/bin/env python3
"""
Execute schema directly using Supabase Management API
Requires service role key for DDL operations
"""

import requests
import os
from typing import Dict, Any

def execute_schema_via_api():
    """Execute schema using Supabase Management API"""
    
    # Read the schema file
    with open('article2audio_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Supabase project details
    project_ref = "qslpqxjoupwyclmguniz"
    
    # Try to get service token from environment
    service_token = os.getenv('SUPABASE_ACCESS_TOKEN', 'sbp_469557386c9ea33c3424e70c9350c07b4d1f5150')
    
    print(f"🔧 Attempting to execute schema for project: {project_ref}")
    print("📝 Using Supabase Management API...")
    
    # Supabase Management API endpoint for SQL execution
    api_url = f"https://api.supabase.com/v1/projects/{project_ref}/database/sql"
    
    headers = {
        'Authorization': f'Bearer {service_token}',
        'Content-Type': 'application/json'
    }
    
    # Split schema into individual statements
    statements = []
    
    # Parse the SQL file into individual statements
    current_statement = []
    for line in schema_sql.split('\n'):
        if line.strip() and not line.strip().startswith('--'):
            current_statement.append(line)
            if line.strip().endswith(';'):
                statement = '\n'.join(current_statement)
                statements.append(statement)
                current_statement = []
    
    print(f"📋 Found {len(statements)} SQL statements to execute")
    
    success_count = 0
    failed_statements = []
    
    for i, statement in enumerate(statements, 1):
        # Skip empty statements
        if not statement.strip():
            continue
            
        print(f"\n[{i}/{len(statements)}] Executing statement...")
        
        # Show first 50 chars of statement
        preview = statement.strip()[:50].replace('\n', ' ')
        print(f"   Preview: {preview}...")
        
        payload = {
            'query': statement
        }
        
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Statement {i} executed successfully")
                success_count += 1
            else:
                print(f"   ❌ Statement {i} failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                failed_statements.append((i, statement[:50], response.text[:200]))
                
        except Exception as e:
            print(f"   ❌ Statement {i} error: {e}")
            failed_statements.append((i, statement[:50], str(e)))
    
    print(f"\n{'='*60}")
    print(f"📊 Execution Summary:")
    print(f"   ✅ Successful: {success_count}/{len(statements)}")
    print(f"   ❌ Failed: {len(failed_statements)}/{len(statements)}")
    
    if failed_statements:
        print(f"\n❌ Failed statements:")
        for idx, preview, error in failed_statements:
            print(f"   Statement {idx}: {preview}")
            print(f"   Error: {error}")
    
    if success_count == len(statements):
        print("\n🎉 Schema executed successfully!")
        return True
    else:
        print("\n⚠️ Some statements failed. Manual execution may be required.")
        print("\n💡 Alternative: Copy the schema SQL to Supabase Dashboard SQL Editor")
        print("   URL: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz/sql")
        return False

if __name__ == "__main__":
    # First try API execution
    success = execute_schema_via_api()
    
    if not success:
        print("\n" + "="*60)
        print("📋 MANUAL EXECUTION REQUIRED")
        print("="*60)
        print("\n1. Go to: https://supabase.com/dashboard/project/qslpqxjoupwyclmguniz/sql")
        print("2. Copy and paste the contents of article2audio_schema.sql")
        print("3. Click 'Run' to execute")
        print("4. Run: python3 verify_schema_execution.py to confirm")