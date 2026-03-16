"""
SQLite database module for employee master data.
Replaces the plain-text employee_master.json with a secure .db file.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'employee_master.db')

def get_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the employees table if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            emp_code TEXT NOT NULL,
            department TEXT DEFAULT '',
            designation TEXT DEFAULT '',
            location TEXT DEFAULT '',
            employment_type TEXT DEFAULT 'Permanent',
            bank_name TEXT DEFAULT '',
            account_number TEXT DEFAULT '',
            pan_number TEXT DEFAULT '',
            esic_number TEXT DEFAULT '',
            pf_number TEXT DEFAULT '',
            hospital_name TEXT DEFAULT 'ASHU EYE HOSPITAL'
        )
    ''')
    conn.commit()
    conn.close()

def get_employee(name):
    """
    Look up an employee by name (case-insensitive).
    Returns a dict with employee details or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM employees WHERE UPPER(name) = UPPER(?)',
        (name.strip(),)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        'emp_code': row['emp_code'],
        'department': row['department'],
        'designation': row['designation'],
        'location': row['location'],
        'employment_type': row['employment_type'],
        'bank_name': row['bank_name'],
        'account_number': row['account_number'],
        'pan_number': row['pan_number'],
        'esic_number': row['esic_number'],
        'pf_number': row['pf_number'],
        'hospital_name': row['hospital_name'],
    }

def get_all_employees():
    """Return all employees as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY name')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def upsert_employee(name, details):
    """Insert or update an employee record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO employees (name, emp_code, department, designation, location,
                               employment_type, bank_name, account_number,
                               pan_number, esic_number, pf_number, hospital_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            emp_code = excluded.emp_code,
            department = excluded.department,
            designation = excluded.designation,
            location = excluded.location,
            employment_type = excluded.employment_type,
            bank_name = excluded.bank_name,
            account_number = excluded.account_number,
            pan_number = excluded.pan_number,
            esic_number = excluded.esic_number,
            pf_number = excluded.pf_number,
            hospital_name = excluded.hospital_name
    ''', (
        name.strip().upper(),
        details.get('emp_code', ''),
        details.get('department', ''),
        details.get('designation', ''),
        details.get('location', ''),
        details.get('employment_type', 'Permanent'),
        details.get('bank_name', ''),
        details.get('account_number', ''),
        details.get('pan_number', ''),
        details.get('esic_number', ''),
        details.get('pf_number', ''),
        details.get('hospital_name', 'ASHU EYE HOSPITAL'),
    ))
    conn.commit()
    conn.close()

def migrate_from_json(json_path=None):
    """
    One-time migration: import data from employee_master.json into SQLite.
    Safe to call multiple times (uses upsert).
    """
    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'employee_master.json')

    if not os.path.exists(json_path):
        print(f"No JSON file found at {json_path}, skipping migration.")
        return 0

    with open(json_path, 'r') as f:
        data = json.load(f)

    count = 0
    for name, details in data.items():
        upsert_employee(name, details)
        count += 1

    print(f"Migrated {count} employees from JSON to SQLite.")
    return count


# Auto-initialize on import
init_db()
