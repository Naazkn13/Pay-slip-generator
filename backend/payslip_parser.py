import pandas as pd
import os
import re
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


def _find_total_salary(df, total_row_idx):
    """
    Read the actual salary total from the sheet.
    Some sheets have the TOTAL label in one row but the numeric data in the
    row immediately above it (Employee_12 pattern). Handle both layouts.
    """
    if total_row_idx is None:
        return 0.0

    val = safe_float(df.iloc[total_row_idx, 7])

    # If the TOTAL label row itself has no value in col H, look one row above.
    if val == 0.0 and total_row_idx > 0:
        val = safe_float(df.iloc[total_row_idx - 1, 7])

    return val


def _extract_month_name(df, total_row_idx):
    """
    Extract month name from the Excel sheet.
    Priority:
    1. Row 3 col A: "Working Days in Month (March)" → extract 'March'
    2. First attendance date cell (row 7, col A) parsed as datetime
    Falls back to empty string.
    """
    # 1. Try extracting from the "Working Days in Month (MonthName)" label
    try:
        label = str(df.iloc[3, 0]).strip()
        match = re.search(r'\((\w+)\)', label)
        if match:
            candidate = match.group(1).capitalize()
            # Validate it looks like a month name (at least 3 alpha chars)
            if len(candidate) >= 3 and candidate.isalpha():
                return candidate
    except Exception:
        pass

    # 2. Try parsing the first attendance date in col A, row 7
    try:
        if total_row_idx and total_row_idx > 7:
            date_val = df.iloc[7, 0]
            if hasattr(date_val, 'strftime'):
                return date_val.strftime('%B')
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

            # --- Row 0: Employee Name ---
            emp_name = str(df.iloc[0, 1]).strip()

            # --- Row 1: Basic Monthly Salary ---
            basic_salary = safe_float(df.iloc[1, 1])

            # --- Scan bottom 20 rows for TOTAL and TOTAL-PT rows ---
            total_row_idx = None
            pt_row_idx = None

            for idx in range(len(df) - 1, max(-1, len(df) - 20), -1):
                col0_val = str(df.iloc[idx, 0]).strip().upper()

                # Exact match "TOTAL" only (not "TOTAL-PT", not "TOTAL-PT+CONVEYANCE")
                if col0_val == "TOTAL":
                    total_row_idx = idx

                # Any row that has both "TOTAL" and "PT" (e.g. TOTAL-PT, TOTAL-PT+CONVEYANCE)
                if "TOTAL" in col0_val and "PT" in col0_val:
                    pt_row_idx = idx

            # --- Read total salary earned for the month ---
            # _find_total_salary handles the case where the TOTAL label row is
            # empty and the actual data is in the row above it (Employee_12 pattern).
            total_salary_for_month = _find_total_salary(df, total_row_idx)

            # --- PT Deduction ---
            # The TOTAL-PT row stores (Total - PT) in column B (index 1).
            # Column H (index 7) on that row is always empty.
            pt_amount = 200.0  # default
            if pt_row_idx is not None:
                net_after_pt = safe_float(df.iloc[pt_row_idx, 1])
                if net_after_pt > 0:
                    computed_pt = total_salary_for_month - net_after_pt
                    # PT is always 200 in India; accept values in [0, 500] as valid
                    pt_amount = computed_pt if 0 <= computed_pt <= 500 else 200.0

            # --- Conveyance ---
            # Skip any row whose label ALSO contains "TOTAL" to avoid picking up
            # the "TOTAL-PT+CONVEYANCE" row (Employee_2 pattern).
            conveyance = 0.0
            for idx in range(len(df) - 1, max(-1, len(df) - 20), -1):
                col0_val = str(df.iloc[idx, 0]).strip().upper()
                if "CONVEYANCE" in col0_val and "TOTAL" not in col0_val:
                    # col B may be a text formula like "30x20"; try col C as fallback
                    val = safe_float(df.iloc[idx, 1])
                    if val == 0.0 and df.shape[1] > 2:
                        val = safe_float(df.iloc[idx, 2])
                    conveyance = val
                    break

            # --- OT / LOP ---
            net_adjustment = total_salary_for_month - basic_salary
            if net_adjustment >= 0:
                ot_amount = round(net_adjustment)
                lop_amount = 0
            else:
                ot_amount = 0
                lop_amount = round(abs(net_adjustment))

            # --- LOP Days count ---
            shift_hours = safe_float(df.iloc[2, 1]) if safe_float(df.iloc[2, 1]) > 0 else 7
            per_day_salary = safe_float(df.iloc[4, 1])
            if per_day_salary == 0:
                per_day_salary = basic_salary / 30

            lop_days = 0.0
            if lop_amount > 0 and total_row_idx is not None and total_row_idx > 7:
                for i in range(7, total_row_idx):
                    work_hours = df.iloc[i, 3]  # col D = Work Hours
                    if pd.isna(work_hours) or str(work_hours).strip() in ("0:00:00", ""):
                        day_str = str(df.iloc[i, 0]).lower()
                        if "sunday" not in day_str and "pl" not in day_str:
                            lop_days += 1
                    else:
                        short_hours = safe_float(df.iloc[i, 6])
                        if short_hours > 0.5:
                            lop_days += (short_hours / shift_hours)

            # --- Final rounding ---
            basic_salary = round(basic_salary)
            ot_amount = round(ot_amount)
            lop_amount = round(lop_amount)
            pt_amount = round(pt_amount)
            conveyance = round(conveyance)

            hra = 0
            da = 0
            pf = 0
            esic = 0
            tds = 0

            total_earnings = basic_salary + hra + da + conveyance + ot_amount
            total_deductions = tds + pf + esic + pt_amount + lop_amount
            net_pay = total_earnings - total_deductions

            # --- Employee master details from SQLite ---
            emp_details = get_employee(emp_name)

            if emp_details is None:
                # Auto-generate EMP code from sheet name (Employee_12 → EMP-012)
                sheet_num = re.search(r'\d+', sheet_name)
                emp_code_num = sheet_num.group().zfill(3) if sheet_num else str(len(all_payslips) + 1).zfill(3)

                emp_details = {
                    "emp_code": f"EMP-{emp_code_num}",
                    "department": "",
                    "designation": "",
                    "location": "",
                    "employment_type": "Full Time",
                    "bank_name": "",
                    "account_number": "",
                    "pan_number": "",
                    "esic_number": "",
                    "pf_number": "",
                    "hospital_name": "ASHU EYE HOSPITAL",
                }

            hospital_name = emp_details.pop('hospital_name', 'ASHU EYE HOSPITAL')
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
