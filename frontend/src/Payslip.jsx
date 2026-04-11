import React, { useRef, useState } from 'react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { Download } from 'lucide-react';

const Payslip = ({ data }) => {
    const payslipRef = useRef();
    const [isDownloading, setIsDownloading] = useState(false);

    if (!data) return null;

    const { employeeName, staticDetails, earnings, deductions, summary } = data;

    // Hospital name is now driven by API data; falls back to a default
    const hospitalName = data.hospitalName || "ASHU EYE HOSPITAL";

    const handleDownloadPdf = async () => {
        const element = payslipRef.current;
        if (!element) return;

        setIsDownloading(true);
        try {
            const canvas = await html2canvas(element, {
                scale: 2,
                useCORS: true,
                allowTaint: true,
                backgroundColor: '#ffffff',
                logging: false,
                imageTimeout: 15000,
            });
            const imgData = canvas.toDataURL('image/png');

            // A4 size: 210 x 297 mm
            const pdf = new jsPDF('p', 'mm', 'a4');
            const pdfWidth = pdf.internal.pageSize.getWidth();
            const pdfHeight = pdf.internal.pageSize.getHeight();

            // Add a horizontal margin (e.g., 10mm from left/right)
            const marginX = 10;
            const drawWidth = pdfWidth - (marginX * 2);
            const drawHeight = (canvas.height * drawWidth) / canvas.width;

            // Calculate vertical center
            const marginY = (pdfHeight - drawHeight) / 2;

            pdf.addImage(imgData, 'PNG', marginX, marginY, drawWidth, drawHeight);

            const safeName = employeeName.replace(/\s+/g, '_');
            const month = summary.monthName || "Unknown";
            pdf.save(`Payslip_${safeName}_${month}_2026.pdf`);
        } catch (error) {
            console.error("Error generating PDF:", error);
        } finally {
            setIsDownloading(false);
        }
    };

    return (
        <div className="mx-auto my-8 w-[800px]">
            {/* Download Button (hidden on print) */}
            <div className="flex justify-end mb-2 no-print">
                <button
                    onClick={handleDownloadPdf}
                    disabled={isDownloading}
                    className="bg-blue-100 hover:bg-blue-200 text-blue-800 border border-blue-300 py-1.5 px-3 rounded shadow-sm text-sm font-semibold flex items-center transition"
                >
                    <Download className="w-4 h-4 mr-1.5" />
                    {isDownloading ? "Generating..." : "Download PDF"}
                </button>
            </div>

            <div ref={payslipRef} className="w-[800px] bg-white border border-black print-page relative text-[12px] text-black" style={{ fontFamily: 'Arial, Helvetica, sans-serif' }}>

                {/* Header Section */}
                <div className="relative pt-2 pb-2 h-[120px]">
                    <div className="text-center font-bold text-[14px] tracking-wide mt-1">
                        {hospitalName}
                    </div>

                    {/* Logo */}
                    <div className="absolute left-3 top-3 w-[260px] h-[80px]">
                        <img src="/logo.png" alt="Hospital Logo" className="w-full h-full object-contain object-left" />
                    </div>

                    <div className="absolute bottom-2 w-full text-center font-bold text-[13px]">
                        Payslip for the Month {summary.monthName || "February"} 2026
                    </div>
                </div>

                {/* Employee Details Section */}
                <div className="flex border-t border-black leading-snug">
                    {/* Left Column */}
                    <div className="w-1/2 border-r border-black p-1 px-2 pb-2">
                        <div className="flex"><div className="w-[110px]">Employee Code</div><div className="w-3">:</div><div className="flex-1">{staticDetails.emp_code || '-'}</div></div>
                        <div className="flex"><div className="w-[110px]">Employee Name</div><div className="w-3">:</div><div className="flex-1 uppercase">{employeeName}</div></div>
                        <div className="flex"><div className="w-[110px]">Department</div><div className="w-3">:</div><div className="flex-1">{staticDetails.department || '-'}</div></div>
                        <div className="flex"><div className="w-[110px]">Designation</div><div className="w-3">:</div><div className="flex-1">{staticDetails.designation || '-'}</div></div>
                        <div className="flex"><div className="w-[110px]">Location</div><div className="w-3">:</div><div className="flex-1">{staticDetails.location || '-'}</div></div>
                        <div className="flex items-start"><div className="w-[110px] leading-tight">Employment<br />Type</div><div className="w-3 mt-3">:</div><div className="flex-1 mt-3">{staticDetails.employment_type || 'Full Time'}</div></div>
                    </div>
                    {/* Right Column */}
                    <div className="w-1/2 p-1 px-2 pb-2">
                        <div className="flex"><div className="w-[100px]">Bank Name</div><div className="w-3">:</div><div className="flex-1">{staticDetails.bank_name || '-'}</div></div>
                        <div className="flex"><div className="w-[100px]">Account Number</div><div className="w-3">:</div><div className="flex-1">{staticDetails.account_number || '-'}</div></div>
                        <div className="flex"><div className="w-[100px]">PAN Number</div><div className="w-3">:</div><div className="flex-1">{staticDetails.pan_number || '-'}</div></div>
                        <div className="flex"><div className="w-[100px]">ESIC Number</div><div className="w-3">:</div><div className="flex-1">{staticDetails.esic_number || '-'}</div></div>
                        <div className="flex"><div className="w-[100px]">PF Number</div><div className="w-3">:</div><div className="flex-1">{staticDetails.pf_number || '-'}</div></div>
                        <div className="flex"><div className="w-[100px]">LOP Days</div><div className="w-3">:</div><div className="flex-1">{summary.lopDays > 0 ? summary.lopDays : '-'}</div></div>
                    </div>
                </div>

                {/* Financials Table */}
                <div className="border-t border-black">
                    {/* Table Header */}
                    <div className="flex border-b border-black font-bold">
                        <div className="w-1/2 flex border-r border-black p-1 px-2">
                            <div className="flex-1">Earnings</div>
                            <div className="w-20 text-right">Amount</div>
                        </div>
                        <div className="w-1/2 flex p-1 px-2">
                            <div className="flex-1">Deductions</div>
                            <div className="w-20 text-right">Amount</div>
                        </div>
                    </div>

                    {/* Table Body */}
                    <div className="flex leading-snug">
                        {/* Earnings List */}
                        <div className="w-1/2 flex flex-col border-r border-black p-1 px-2 pb-8">
                            <div className="flex justify-between"><div className="flex-1">Basic</div><div className="w-20 text-right">{earnings.basicSalary % 1 === 0 ? earnings.basicSalary : earnings.basicSalary.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">HRA</div><div className="w-20 text-right">{earnings.hra % 1 === 0 ? earnings.hra : earnings.hra.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">DA</div><div className="w-20 text-right">{earnings.da % 1 === 0 ? earnings.da : earnings.da.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">Conveyance</div><div className="w-20 text-right">{earnings.conveyance % 1 === 0 ? earnings.conveyance : earnings.conveyance.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">OT</div><div className="w-20 text-right">{earnings.ot % 1 === 0 ? earnings.ot : earnings.ot.toFixed(2)}</div></div>
                        </div>
                        {/* Deductions List */}
                        <div className="w-1/2 flex flex-col p-1 px-2 pb-8">
                            <div className="flex justify-between"><div className="flex-1">TDS</div><div className="w-20 text-right">{deductions.tds % 1 === 0 ? deductions.tds : deductions.tds.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">PF</div><div className="w-20 text-right">{deductions.pf % 1 === 0 ? deductions.pf : deductions.pf.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">ESIC</div><div className="w-20 text-right">{deductions.esic % 1 === 0 ? deductions.esic : deductions.esic.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">PT</div><div className="w-20 text-right">{deductions.pt % 1 === 0 ? deductions.pt : deductions.pt.toFixed(2)}</div></div>
                            <div className="flex justify-between"><div className="flex-1">LOP</div><div className="w-20 text-right">{deductions.lop % 1 === 0 ? deductions.lop : deductions.lop.toFixed(2)}</div></div>
                        </div>
                    </div>

                    {/* Totals Row */}
                    <div className="flex border-t border-black font-bold">
                        <div className="w-1/2 flex border-r border-black">
                            <div className="flex-1 p-1 px-2 border-r border-black">Total Earnings (in Rs.)</div>
                            <div className="w-24 text-right p-1 px-2 font-normal">{summary.totalEarnings % 1 === 0 ? summary.totalEarnings : summary.totalEarnings.toFixed(2)}</div>
                        </div>
                        <div className="w-1/2 flex">
                            <div className="flex-1 p-1 px-2 border-r border-black">Total Deductions (in Rs.)</div>
                            <div className="w-24 text-right p-1 px-2 font-normal">{summary.totalDeductions % 1 === 0 ? summary.totalDeductions : summary.totalDeductions.toFixed(2)}</div>
                        </div>
                    </div>
                </div>

                {/* Net Pay Section */}
                <div className="border-t border-black p-1 px-2 pb-2 leading-relaxed">
                    <div className="flex mt-1">
                        <span className="mr-1">Net Pay for the month ( Total Earnings - Total Deductions):</span>
                        <span className="font-bold ml-8">{summary.netPay % 1 === 0 ? summary.netPay : summary.netPay.toFixed(2)}</span>
                    </div>
                    <div className="mt-2 text-[12px] pb-1">
                        {summary.netPayWords}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Payslip;
