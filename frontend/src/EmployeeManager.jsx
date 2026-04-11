import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, X, Save, Plus, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '';

const EMPTY_FORM = {
  name: '',
  emp_code: '',
  department: '',
  designation: '',
  location: '',
  employment_type: 'Full Time',
  bank_name: '',
  account_number: '',
  pan_number: '',
  esic_number: '',
  pf_number: '',
  hospital_name: 'ASHU EYE HOSPITAL',
};

const EmployeeManager = () => {
  const [open, setOpen] = useState(false);
  const [employees, setEmployees] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editing, setEditing] = useState(null); // name of employee being edited
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState(null);

  const fetchEmployees = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/employees`);
      setEmployees(res.data.employees || []);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    if (open) fetchEmployees();
  }, [open]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleEdit = (emp) => {
    setEditing(emp.name);
    setForm({
      name: emp.name,
      emp_code: emp.emp_code || '',
      department: emp.department || '',
      designation: emp.designation || '',
      location: emp.location || '',
      employment_type: emp.employment_type || 'Full Time',
      bank_name: emp.bank_name || '',
      account_number: emp.account_number || '',
      pan_number: emp.pan_number || '',
      esic_number: emp.esic_number || '',
      pf_number: emp.pf_number || '',
      hospital_name: emp.hospital_name || 'ASHU EYE HOSPITAL',
    });
  };

  const handleNew = () => {
    setEditing('__new__');
    setForm(EMPTY_FORM);
  };

  const handleSave = async () => {
    if (!form.name.trim()) {
      setMsg({ type: 'error', text: 'Employee name is required.' });
      return;
    }
    setSaving(true);
    setMsg(null);
    try {
      await axios.post(`${API_BASE}/api/employees`, form);
      setMsg({ type: 'success', text: 'Employee saved!' });
      setEditing(null);
      fetchEmployees();
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Save failed.' });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setEditing(null);
    setForm(EMPTY_FORM);
    setMsg(null);
  };

  const fields = [
    { key: 'name', label: 'Employee Name', required: true },
    { key: 'emp_code', label: 'Employee Code' },
    { key: 'department', label: 'Department' },
    { key: 'designation', label: 'Designation' },
    { key: 'location', label: 'Location' },
    { key: 'employment_type', label: 'Employment Type' },
    { key: 'bank_name', label: 'Bank Name' },
    { key: 'account_number', label: 'Account Number' },
    { key: 'pan_number', label: 'PAN Number' },
    { key: 'esic_number', label: 'ESIC Number' },
    { key: 'pf_number', label: 'PF Number' },
    { key: 'hospital_name', label: 'Hospital Name' },
  ];

  return (
    <div className="w-full max-w-4xl mx-auto mt-4 px-4">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between bg-white border border-gray-200 rounded-xl shadow-sm p-4 hover:bg-gray-50 transition"
      >
        <div className="flex items-center gap-2 text-blue-800 font-semibold">
          <Users className="w-5 h-5" />
          Employee Master (Bank &amp; Details)
        </div>
        {open ? <ChevronUp className="w-4 h-4 text-gray-500" /> : <ChevronDown className="w-4 h-4 text-gray-500" />}
      </button>

      {open && (
        <div className="bg-white border border-gray-200 rounded-b-xl shadow-sm p-6 -mt-1">

          {/* Employee List */}
          {employees.length > 0 && editing === null && (
            <div className="mb-4">
              <p className="text-sm text-gray-500 mb-2">Click an employee to edit their details:</p>
              <div className="grid grid-cols-1 gap-2">
                {employees.map((emp) => (
                  <button
                    key={emp.name}
                    onClick={() => handleEdit(emp)}
                    className="text-left flex justify-between items-center border border-gray-100 rounded-lg p-3 hover:bg-blue-50 hover:border-blue-200 transition"
                  >
                    <span className="font-medium text-gray-800">{emp.name}</span>
                    <span className="text-xs text-gray-400">{emp.emp_code}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {employees.length === 0 && editing === null && (
            <p className="text-sm text-gray-500 mb-4">No employees found. Add one to start populating bank and personal details on payslips.</p>
          )}

          {/* Add New Button */}
          {editing === null && (
            <button
              onClick={handleNew}
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition"
            >
              <Plus className="w-4 h-4" />
              Add Employee
            </button>
          )}

          {/* Form */}
          {editing !== null && (
            <div>
              <h3 className="text-md font-semibold text-gray-700 mb-4">
                {editing === '__new__' ? 'New Employee' : `Editing: ${editing}`}
              </h3>
              <div className="grid grid-cols-2 gap-x-6 gap-y-3">
                {fields.map(({ key, label, required }) => (
                  <div key={key}>
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                      {label}{required && <span className="text-red-500 ml-0.5">*</span>}
                    </label>
                    <input
                      type="text"
                      name={key}
                      value={form[key]}
                      onChange={handleChange}
                      className="w-full border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
                      placeholder={label}
                    />
                  </div>
                ))}
              </div>

              {msg && (
                <p className={`mt-3 text-sm font-medium ${msg.type === 'error' ? 'text-red-600' : 'text-green-600'}`}>
                  {msg.text}
                </p>
              )}

              <div className="flex gap-3 mt-4">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="flex items-center gap-1.5 bg-green-600 hover:bg-green-700 disabled:bg-green-300 text-white text-sm font-semibold px-4 py-2 rounded-lg transition"
                >
                  <Save className="w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Employee'}
                </button>
                <button
                  onClick={handleCancel}
                  className="flex items-center gap-1.5 border border-gray-300 text-gray-600 hover:bg-gray-50 text-sm font-semibold px-4 py-2 rounded-lg transition"
                >
                  <X className="w-4 h-4" />
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmployeeManager;
