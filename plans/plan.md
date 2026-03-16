# Payslip Generator Project Plan

Based on the analysis of the provided UI images and the structure of `Emp pay sheet.xlsx`, here is the detailed step-by-step plan to proceed:

## Phase 1: Preparation and Backend Setup
1. **Initialize Backend Environment**: Create a Python virtual environment and install necessary libraries (`pandas`, `openpyxl`, `Flask`, `flask-cors`).
2. **Employee Master Data Strategy**: Since static details (like Bank Name, PAN, PF number) are not in the monthly timesheet, we will create a local configuration file (e.g., `employee_master.json`) to store these details per employee.
3. **Data Extraction Logic (`parser.py`)**:
   - Write a function to iterate through all sheets (`Employee_1`, `Employee_2`, etc.) in the uploaded Excel.
   - Extract **Employee Name** and **Basic Monthly Salary**.
   - Calculate totals from the bottom rows to find **OT amount**, **LOP**, and **PT** (Professional Tax).
   - Calculate **Net Pay** based on the formula: `Net Pay = Basic + OT - LOP - PT`.
4. **API Development (`app.py`)**: Create a Flask endpoint (`/api/upload`) that accepts an Excel file, runs the extraction logic, and returns a JSON list of all employee payslip data.

## Phase 2: Frontend Setup and UI Development
1. **Initialize Frontend App**: Create a React application using Vite (`npx create-vite`).
2. **Upload Interface**: Build a clean UI to upload the monthly Excel file and display a success message / loading state.
3. **Payslip Component Design**:
   - Create a `Payslip.jsx` component that accurately mirrors the visual layout of the JPEG images.
   - Implement the grid layout for the "Employee Details" and "Bank Details" sections.
   - Implement the side-by-side Earnings and Deductions tables.
   - Map JSON properties (from the backend) to the respective UI fields dynamically.
4. **Dashboard Integration**: Read the parsed JSON response from the API and allow the user to view/generate the payslip for each employee from a list.
5. **Print/PDF functionality**: Add a "Print Payslip" button using `window.print()` combined with `@media print` CSS rules to generate pixel-perfect PDFs.

## Next Actionable Steps for Implementation:
- Confirm how strictly the static fields (Bank, PAN, PF, ESIC) need to be handled (mocked or via a master file).
- Proceed to implement Phase 1.
