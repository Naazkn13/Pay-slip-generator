# 💰 Payroll Slip Generator

Payroll automation tool that processes multi-sheet Excel salary data and generates company-formatted employee payslips in bulk.

---

## ⚡ Features

- Upload Excel payroll file
- Support for multiple Excel sheets
- Bulk payslip generation for all employees
- Salary calculation based on backend rules
- Company-specific payslip layout
- PDF payslip output
- Employee-wise payslip generation

---

## ⚠️ Current Limitation

Employee master details such as employee ID, name, account number, and PAN number are currently hardcoded.

Planned improvement: move employee master data to database or Excel-based configuration.

---

## 🧠 Tech Stack

### Frontend
- React / Next.js

### Backend
- Python / APIs

### Data Processing
- Excel Parsing
- Salary Rule Engine
- Bulk PDF Generation

---

## 📊 Workflow

```text
Multi-sheet Excel Payroll File
        ↓
Backend Salary Rule Processing
        ↓
Bulk Payslip Generation
        ↓
Employee-wise PDF Output
