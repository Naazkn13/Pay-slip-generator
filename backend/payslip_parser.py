import pandas as pd
import os
import math
from database import get_employee


def safe_float(val):
    """Safely convert a value to float, returning 0.0 on failure."""
    if pd.isna(val) or val == 'nan':
        return 0.0
    try:
        if isinstance(val, str):
            val = val.replace(',', '')
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def num_to_words(n):
    """Convert a numeric rupee amount to words."""
    if n == 0:
        return "Zero Rupees Only"
    try:
        from num2words import num2words
        rupees = int(n)
        paise = int(round((n - rupees) * 100))
        words = num2words(rupees, lang='en_IN').title()

        if paise > 0:
            paise_words = num2words(paise, lang='en_IN').title()
            return f"{words} Rupees and {paise_words} Paise Only"
        else:
            return f"{words} Rupees Only"
    except ImportError:
        return f"{n} Rupees Only (Install num2words)"


def parse_excel(file_stream):
    """
    Parses the Excel file and extracts payslip data for all employees.
    Each sheet = one employee's attendance+salary data.
    """
    excel_file = pd.ExcelFile(file_stream)

    all_payslips = []

    for sheet_name in excel_file.sheet_names:
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

            if df.empty or len(df) < 5:
                continue

            # Extract basic data
            emp_name = str(df.iloc[0, 1]).strip()

            # Row 1 = Basic Monthly Salary
            basic_salary = safe_float(df.iloc[1, 1])

            # Bottom rows: find TOTAL and PT rows
            total_row_idx = None
            pt_row_idx = None

            for idx in range(len(df) - 1, max(-1, len(df) - 20), -1):
                col0_val = str(df.iloc[idx, 0]).strip().upper()
                if col0_val == "TOTAL":
                    total_row_idx = idx
                if "TOTAL" in col0_val and "PT" in col0_val:
                    pt_row_idx = idx

            total_salary_for_month = 0.0
            pt_amount = 0.0

            if total_row_idx is not None:
                total_salary_for_month = safe_float(df.iloc[total_row_idx, 7])

            if pt_row_idx is not None:
                pt_amount = total_salary_for_month - safe_float(df.iloc[pt_row_idx, 7])
                if pt_amount < 0:
                    pt_amount = 200  # Fallback
            else:
                pt_amount = 200  # Standard fallback

            # Extract conveyance
            conveyance = 0
            for idx in range(len(df) - 1, max(-1, len(df) - 20), -1):
                col0_val = str(df.iloc[idx, 0]).strip().upper()
                if "CONVEYANCE" in col0_val:
                    conveyance = safe_float(df.iloc[idx, 1])
                    break

            # --- NET OT / LOP CALCULATION ---
            net_adjustment = total_salary_for_month - basic_salary

            if net_adjustment >= 0:
                ot_amount = round(net_adjustment)
                lop_amount = 0
            else:
                ot_amount = 0
                lop_amount = round(abs(net_adjustment))

            # Count LOP Days
            shift_hours = safe_float(df.iloc[2, 1]) if safe_float(df.iloc[2, 1]) > 0 else 7
            per_day_salary = safe_float(df.iloc[4, 1])
            if per_day_salary == 0:
                per_day_salary = basic_salary / 30

            lop_days = 0
            if lop_amount > 0 and total_row_idx is not None and total_row_idx > 7:
                for i in range(7, total_row_idx):
                    work_hours = df.iloc[i, 3]  # col D
                    if pd.isna(work_hours) or str(work_hours).strip() in ("0:00:00", ""):
                        day_str = str(df.iloc[i, 0]).lower()
                        if "sunday" not in day_str and "pl" not in day_str:
                            lop_days += 1
                    else:
                        short_hours = safe_float(df.iloc[i, 6])
                        if short_hours > 0.5:
                            lop_days += (short_hours / shift_hours)

            # Final rounding
            basic_salary = round(basic_salary)
            ot_amount = round(ot_amount)
            lop_amount = round(lop_amount)
            pt_amount = round(pt_amount)
            conveyance = round(conveyance)

            # Fixed values
            hra = 0
            da = 0
            pf = 0
            esic = 0
            tds = 0

            total_earnings = basic_salary + hra + da + conveyance + ot_amount
            total_deductions = tds + pf + esic + pt_amount + lop_amount

            net_pay = total_earnings - total_deductions

            # Pull employee details from SQLite database
            emp_details = get_employee(emp_name)

            if emp_details is None:
                # Fallback for unknown employees
                emp_details = {
                    "emp_code": f"EMP-{len(all_payslips)+1:03d}",
                    "department": "-",
                    "designation": "-",
                    "location": "-",
                    "employment_type": "Full Time",
                    "bank_name": "-",
                    "account_number": "-",
                    "pan_number": "-",
                    "esic_number": "-",
                    "pf_number": "-",
                    "hospital_name": "ASHU EYE HOSPITAL",
                }

            # Extract hospital_name before removing it from static details
            hospital_name = emp_details.pop('hospital_name', 'ASHU EYE HOSPITAL')

            # Try to extract month name from sheet data
            month_name = _extract_month_name(df, total_row_idx)

            payslip = {
                "employeeName": emp_name,
                "hospitalName": hospital_name,
                "staticDetails": emp_details,
                "earnings": {
                    "basicSalary": basic_salary,
                    "hra": hra,
                    "da": da,
                    "conveyance": conveyance,
                    "ot": ot_amount
                },
                "deductions": {
                    "tds": tds,
                    "pf": pf,
                    "esic": esic,
                    "pt": pt_amount,
                    "lop": lop_amount
                },
                "summary": {
                    "totalEarnings": total_earnings,
                    "totalDeductions": total_deductions,
                    "netPay": net_pay,
                    "netPayWords": num_to_words(net_pay),
                    "lopDays": round(lop_days, 1),
                    "monthName": month_name,
                }
            }

            all_payslips.append(payslip)

        except Exception as sheet_e:
            print(f"Error processing sheet '{sheet_name}': {sheet_e}")
            import traceback
            traceback.print_exc()

    return all_payslips


def _extract_month_name(df, total_row_idx):
    """
    Attempt to extract the month name from dates in the attendance rows.
    Falls back to empty string if not determinable.
    """
    try:
        if total_row_idx and total_row_idx > 7:
            # Row 7 is usually the first attendance day
            date_val = df.iloc[7, 0]
            if hasattr(date_val, 'strftime'):
                return date_val.strftime('%B')
            # Try parsing as string
            date_str = str(date_val).strip()
            if len(date_str) > 3:
                import datetime
                for fmt in ('%d-%m-%Y', '%Y-%m-%d', '%d/%m/%Y'):
                    try:
                        dt = datetime.datetime.strptime(date_str[:10], fmt)
                        return dt.strftime('%B')
                    except ValueError:
                        continue
    except Exception:
        pass
    return ""
