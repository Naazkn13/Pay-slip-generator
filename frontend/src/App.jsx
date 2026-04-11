import React, { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, Printer, CheckCircle, AlertCircle } from 'lucide-react';
import Payslip from './Payslip';
import EmployeeManager from './EmployeeManager';

const API_BASE = import.meta.env.VITE_API_URL || '';

function App() {
  const [file, setFile] = useState(null);
  const [payslips, setPayslips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [newEmployees, setNewEmployees] = useState([]);
  const employeeManagerRef = useRef(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setNewEmployees([]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an Excel file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setNewEmployees([]);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setPayslips(response.data.data);

      // If new employees were auto-registered, tell the user to fill in details
      if (response.data.newEmployees && response.data.newEmployees.length > 0) {
        setNewEmployees(response.data.newEmployees);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Error connecting to backend");
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Navbar */}
      <nav className="bg-blue-900 text-white p-4 shadow-md no-print sticky top-0 z-50">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">Payslip Generator Pro</h1>
          {payslips.length > 0 && (
            <button
              onClick={handlePrint}
              className="bg-white text-blue-900 px-4 py-2 rounded-md font-semibold flex items-center hover:bg-blue-50 transition"
            >
              <Printer className="w-5 h-5 mr-2" />
              Print All Payslips
            </button>
          )}
        </div>
      </nav>

      {/* Employee Master Panel */}
      <div className="no-print" ref={employeeManagerRef}>
        <EmployeeManager />
      </div>

      {/* Upload Section */}
      <main className="max-w-4xl mx-auto mt-4 px-4 no-print">

        {/* New-employee banner */}
        {newEmployees.length > 0 && (
          <div className="mb-4 bg-amber-50 border border-amber-300 rounded-xl p-4 flex gap-3">
            <AlertCircle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-amber-800 text-sm">
                {newEmployees.length} new employee{newEmployees.length > 1 ? 's' : ''} detected and registered:
              </p>
              <ul className="mt-1 list-disc list-inside text-amber-700 text-sm">
                {newEmployees.map(n => <li key={n}>{n}</li>)}
              </ul>
              <p className="mt-2 text-amber-700 text-sm">
                Open <strong>Employee Master</strong> above to fill in their Bank Name, Account Number, PAN, ESIC and PF details.
                Those details will appear on payslips from the next upload onwards.
              </p>
            </div>
          </div>
        )}

        <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center space-y-4">
          <div className="bg-blue-50 p-4 rounded-full text-blue-500 mb-2">
            <UploadCloud size={48} />
          </div>
          <h2 className="text-2xl font-semibold text-gray-800">Upload Monthly Attendance Excel</h2>
          <p className="text-gray-500 text-center max-w-md">
            Select the <strong className="font-semibold text-gray-700">Emp pay sheet.xlsx</strong> to automatically generate printable payslips for all employees.
          </p>

          <div className="w-full max-w-md border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition mt-4">
            <input
              type="file"
              accept=".xlsx, .xls"
              onChange={handleFileChange}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          {file && (
            <div className="flex items-center text-green-600 mt-2">
              <CheckCircle className="w-5 h-5 mr-2" />
              <span className="font-medium text-sm">{file.name} selected</span>
            </div>
          )}

          {error && (
            <div className="text-red-500 bg-red-50 p-3 rounded-md w-full max-w-md text-center text-sm font-medium border border-red-200">
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className={`mt-6 w-full max-w-md py-3 rounded-md text-white font-bold text-lg shadow-md transition ${!file || loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? "Processing..." : "Generate Payslips"}
          </button>
        </div>
      </main>

      {/* Payslips */}
      <div className="mt-12 flex flex-col items-center relative z-10">
        {payslips.map((data, idx) => (
          <Payslip key={idx} data={data} />
        ))}
      </div>
    </div>
  );
}

export default App;
