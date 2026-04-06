import React, { useState, useEffect, useRef } from 'react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';

/**
 * SMART AI SPREADSHEET PRO (v6.2)
 * Final Fixed Version with Vercel Env Support & Key Rotation
 */

function App() {
  const [inputText, setInputText] = useState("");
  const [searchTerm, setSearchTerm] = useState(""); 
  const [tableTitle, setTableTitle] = useState("");
  const [columns, setColumns] = useState(["SI No", "Name", "Description", "Status"]);
  const [rows, setRows] = useState(Array.from({ length: 5 }, (_, i) => ({ "SI No": i + 1 })));
  const [history, setHistory] = useState([]);
  const [currentTableId, setCurrentTableId] = useState(null); 
  const [isLoading, setIsLoading] = useState(false);

  // --- API KEYS LOGIC: VERCEL ENV FIRST, THEN INTERNAL ---
  const API_KEYS = [
    process.env.REACT_APP_GEMINI_KEY_1, // Vercel Environment Variable 1
    process.env.REACT_APP_GEMINI_KEY_2, // Vercel Environment Variable 2
    process.env.REACT_APP_GEMINI_KEY_3, // Vercel Environment Variable 3
    "YOUR_INTERNAL_KEY_HERE"             // Backup Internal Key
  ].filter(key => key && key !== "" && key !== "YOUR_INTERNAL_KEY_HERE"); 

  useEffect(() => {
    const saved = localStorage.getItem('ai_sheet_data');
    const savedHistory = localStorage.getItem('ai_sheet_history');
    if (saved) {
      const parsed = JSON.parse(saved);
      setColumns(parsed.columns);
      setRows(parsed.rows);
      setTableTitle(parsed.title || "");
      setCurrentTableId(parsed.id || null);
    }
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, []);

  useEffect(() => {
    localStorage.setItem('ai_sheet_data', JSON.stringify({ id: currentTableId, columns, rows, title: tableTitle }));
    if (currentTableId) {
      const updatedHistory = history.map(item => 
        item.id === currentTableId 
        ? { ...item, columns, rows, title: tableTitle, date: new Date().toLocaleString() } 
        : item
      );
      if (JSON.stringify(updatedHistory) !== JSON.stringify(history)) {
        setHistory(updatedHistory);
        localStorage.setItem('ai_sheet_history', JSON.stringify(updatedHistory));
      }
    }
  }, [columns, rows, tableTitle, currentTableId, history]);

  // --- UPDATED AI LOGIC WITH KEY ROTATION & ERROR HANDLING ---
  const processAICommand = async () => {
    if (!inputText) return;
    
    // Check if keys exist
    if (API_KEYS.length === 0) {
        alert("API Key missing! Please add REACT_APP_GEMINI_KEY_1 in Vercel settings.");
        return;
    }

    setIsLoading(true);
    let apiSuccess = false;
    let quotaExceeded = false;

    // Loop through all keys (Vercel keys first)
    for (let i = 0; i < API_KEYS.length; i++) {
      try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=${API_KEYS[i]}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{
              parts: [{
                text: `Generate spreadsheet data for: "${inputText}". 
                Return ONLY a clean JSON object with "columns" (array of strings) and "rows" (array of objects). 
                Each row must have "SI No" starting from 1. 
                Output must be valid JSON without any Markdown formatting like code blocks.`
              }]
            }]
          })
        });

        const data = await response.json();

        // 429 means Rate Limit - Try next key
        if (response.status === 429) {
          console.warn(`Vercel Key ${i+1} limit reached. Trying next...`);
          quotaExceeded = true;
          continue; 
        }
        
        if (response.ok && data.candidates?.[0]?.content?.parts?.[0]?.text) {
          let rawText = data.candidates[0].content.parts[0].text;
          rawText = rawText.replace(/```json/g, "").replace(/```/g, "").trim();
          
          const cleanJson = JSON.parse(rawText);
          if (cleanJson.columns && cleanJson.rows) {
            setColumns(cleanJson.columns);
            setRows(cleanJson.rows);
            setTableTitle(inputText.toUpperCase());
            setCurrentTableId(null); 
            setInputText("");
            apiSuccess = true;
            break; 
          }
        }
      } catch (error) {
        console.error(`Error with Key ${i+1}:`, error);
      }
    }

    if (!apiSuccess) {
      if (quotaExceeded) {
        alert("All API keys are exhausted. Please wait 1 minute.");
      } else {
        alert("AI processing error. Falling back to local logic.");
      }
      
      const text = inputText.toLowerCase();
      let newCols = ["SI No", "Item", "Details", "Status"];
      if (text.includes("student")) newCols = ["SI No", "Student Name", "Roll ID", "Class", "Result", "Fees"];
      if (text.includes("salary")) newCols = ["SI No", "Employee Name", "Basic", "Overtime", "Bonus %", "Total Salary"];
      
      setColumns(newCols);
      setRows(Array.from({ length: 5 }, (_, i) => {
        const row = { "SI No": i + 1 };
        newCols.slice(1).forEach(c => row[c] = "");
        return row;
      }));
    }
    setIsLoading(false);
  };

  const handleCellChange = (rIdx, col, val) => {
    const updatedRows = [...rows];
    updatedRows[rIdx][col] = val;
    if (col === "Basic" || col === "Overtime" || col === "Bonus %") {
      const basic = parseFloat(updatedRows[rIdx]["Basic"]) || 0;
      const ot = parseFloat(updatedRows[rIdx]["Overtime"]) || 0;
      const bonus = parseFloat(updatedRows[rIdx]["Bonus %"]) || 0;
      updatedRows[rIdx]["Total Salary"] = (basic + ot + (basic * bonus / 100)).toFixed(2);
    }
    setRows(updatedRows);
  };

  const getColumnTotal = (colName) => {
    if (colName === "SI No") return "TOTAL";
    const total = rows.reduce((sum, row) => {
      const val = parseFloat(row[colName]);
      return isNaN(val) ? sum : sum + val;
    }, 0);
    return total === 0 ? "" : total.toLocaleString();
  };

  const deleteRow = (idx) => {
    const updatedRows = rows.filter((_, i) => i !== idx).map((row, i) => ({ ...row, "SI No": i + 1 }));
    setRows(updatedRows);
  };

  const deleteColumn = (colName) => {
    if (colName === "SI No") return;
    if (window.confirm(`Delete column "${colName}"?`)) {
      setColumns(columns.filter(c => c !== colName));
      setRows(rows.map(row => {
        const newRow = { ...row };
        delete newRow[colName];
        return newRow;
      }));
    }
  };

  const saveToHistory = () => {
    if (currentTableId) { alert("Table already synced! ✅"); return; }
    const id = Date.now();
    const newEntry = { id, title: tableTitle || "Untitled Table", date: new Date().toLocaleString(), columns, rows };
    setHistory([newEntry, ...history]);
    setCurrentTableId(id);
    localStorage.setItem('ai_sheet_history', JSON.stringify([newEntry, ...history]));
    alert("Saved to History! ✅");
  };

  const deleteHistoryItem = (e, id) => {
    e.stopPropagation();
    if (window.confirm("Delete?")) {
      const updated = history.filter(item => item.id !== id);
      setHistory(updated);
      localStorage.setItem('ai_sheet_history', JSON.stringify(updated));
      if (currentTableId === id) setCurrentTableId(null);
    }
  };

  const downloadPDF = () => {
    const doc = new jsPDF('p', 'mm', 'a4');
    doc.text(tableTitle || "Smart AI Report", 14, 15);
    autoTable(doc, { startY: 25, head: [columns], body: rows.map(row => columns.map(c => row[c] || "")), theme: 'grid' });
    doc.save(`${tableTitle || 'Report'}.pdf`);
  };

  const downloadExcel = () => {
    const worksheet = XLSX.utils.json_to_sheet(rows);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Sheet1");
    XLSX.writeFile(workbook, `${tableTitle || 'AI_Spreadsheet'}.xlsx`);
  };

  const addColumn = () => {
    const name = prompt("Column Name:");
    if (name) setColumns([...columns, name]);
  };

  const clearTable = () => {
    if (window.confirm("Clear?")) { setRows([{ "SI No": 1 }]); setTableTitle(""); setCurrentTableId(null); }
  };

  const filteredRows = rows.filter(row => 
    Object.values(row).some(val => String(val).toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const getCellClassName = (col, value) => {
    let base = "w-full bg-transparent px-2 py-2 outline-none text-sm min-w-[120px] transition-all focus:bg-slate-700/50 ";
    if (col === "SI No") return base + "text-blue-400 font-bold min-w-[50px] text-center";
    if (col === "Total Salary") return base + "text-emerald-400 font-black";
    const val = String(value).toLowerCase();
    if (["paid", "success", "done"].includes(val)) return base + "text-emerald-400 font-bold";
    if (["pending", "due"].includes(val)) return base + "text-amber-400 font-bold";
    if (["failed", "absent"].includes(val)) return base + "text-red-400 font-bold";
    return base + "text-slate-200";
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 p-2 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-4 gap-4 md:gap-6">
        <div className="lg:col-span-3 order-1">
          <header className="flex flex-col md:flex-row justify-between items-center mb-6 bg-slate-800 p-4 md:p-6 rounded-2xl border border-slate-700 shadow-xl gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-black bg-gradient-to-r from-blue-400 via-emerald-400 to-indigo-400 bg-clip-text text-transparent italic">SMART SPREADSHEET AI</h1>
              <p className="text-[10px] text-slate-500 font-bold tracking-widest mt-1">PRO VERSION v6.2</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              <button onClick={saveToHistory} className={`${currentTableId ? 'bg-emerald-600' : 'bg-blue-600'} px-3 py-2 rounded-lg font-bold text-xs`}>
                {currentTableId ? "SYNCED" : "SAVE"}
              </button>
              <button onClick={downloadExcel} className="bg-emerald-600 px-3 py-2 rounded-lg font-bold text-xs">EXCEL</button>
              <button onClick={downloadPDF} className="bg-indigo-600 px-3 py-2 rounded-lg font-bold text-xs">PDF</button>
            </div>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
             <div className="bg-slate-800 p-3 rounded-xl border border-slate-700 flex gap-2 shadow-lg">
                <input type="text" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 outline-none text-sm" placeholder="Ask AI (e.g. 5 mobile list)..." value={inputText} onChange={(e) => setInputText(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && processAICommand()} />
                <button onClick={processAICommand} disabled={isLoading} className="bg-emerald-500 text-slate-900 px-4 py-2 rounded-lg font-bold">
                  {isLoading ? "..." : "RUN"}
                </button>
             </div>
             <div className="bg-slate-800 p-3 rounded-xl border border-slate-700 flex gap-2">
                <input type="text" className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 outline-none text-sm" placeholder="Search data..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
                <span className="flex items-center px-2">🔍</span>
             </div>
          </div>

          <div className="bg-slate-800 p-4 rounded-xl mb-4 border border-slate-700 flex justify-between items-center">
              <input type="text" className="flex-1 bg-transparent border-none outline-none text-xl font-bold text-emerald-400" placeholder="Table Name..." value={tableTitle} onChange={(e) => setTableTitle(e.target.value)} />
              <button onClick={clearTable} className="text-xs font-bold text-red-500 border border-red-900/30 px-3 py-1 rounded">CLEAR</button>
          </div>

          <div className="bg-slate-800 rounded-2xl shadow-2xl overflow-hidden border border-slate-700 relative">
            {isLoading && (
              <div className="absolute inset-0 bg-slate-900/60 z-20 flex items-center justify-center backdrop-blur-sm">
                <div className="text-emerald-400 font-bold animate-bounce text-sm">AI IS THINKING...</div>
              </div>
            )}
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-700">
                  <tr>
                    {columns.map((col, i) => (
                      <th key={i} onClick={() => deleteColumn(col)} className="px-4 py-4 text-xs font-black uppercase border-r border-slate-600 cursor-pointer hover:bg-red-500/20 group transition-all min-w-[120px]">
                        {col} <span className="text-red-400 ml-1 opacity-0 group-hover:opacity-100">✖</span>
                      </th>
                    ))}
                    <th className="px-4 py-4 text-center w-[60px]">
                      <button onClick={addColumn} className="bg-emerald-600 h-8 w-8 rounded-full font-bold">+</button>
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {filteredRows.map((row, rIdx) => (
                    <tr key={rIdx} className="hover:bg-slate-700/30 group">
                      {columns.map((col, cIdx) => (
                        <td key={cIdx} className="border-r border-slate-700/50">
                          <input type="text" value={row[col] || ""} onChange={(e) => handleCellChange(rIdx, col, e.target.value)} disabled={col === "SI No" || col === "Total Salary"} className={getCellClassName(col, row[col])} />
                        </td>
                      ))}
                      <td className="text-center">
                        <button onClick={() => deleteRow(rIdx)} className="opacity-0 group-hover:opacity-100 text-red-500 font-bold px-2">✖</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot className="bg-slate-900 font-bold border-t-2 border-slate-700">
                  <tr>
                    {columns.map((col, i) => (
                      <td key={i} className="px-4 py-3 text-sm text-emerald-400 border-r border-slate-700">
                        {getColumnTotal(col)}
                      </td>
                    ))}
                    <td className="bg-slate-800/50"></td>
                  </tr>
                </tfoot>
              </table>
            </div>
            <div className="p-4 flex justify-between items-center text-xs text-slate-500">
              <button onClick={() => setRows([...rows, { "SI No": rows.length + 1 }])} className="text-blue-400 font-bold hover:underline">+ ADD NEW ROW</button>
              <div className="uppercase tracking-widest">Entries: {filteredRows.length}</div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-1 order-2 bg-slate-800 rounded-2xl p-4 border border-slate-700 h-[500px] lg:h-auto overflow-y-auto shadow-xl">
          <h2 className="text-md font-bold text-emerald-400 uppercase mb-4 border-b border-slate-700 pb-2">History</h2>
          <div className="space-y-3">
            {history.length === 0 && <p className="text-xs text-slate-600 text-center py-10">No history found</p>}
            {history.map((item) => (
              <div key={item.id} onClick={() => { setColumns(item.columns); setRows(item.rows); setTableTitle(item.title); setCurrentTableId(item.id); }} className={`group bg-slate-900 p-3 rounded-xl border ${currentTableId === item.id ? 'border-emerald-500' : 'border-slate-700'} cursor-pointer hover:border-blue-500 relative transition-all`}>
                <h4 className="font-bold text-slate-200 truncate pr-4 text-xs">{item.title}</h4>
                <p className="text-[9px] text-slate-500 mt-1">{item.date}</p>
                <button onClick={(e) => deleteHistoryItem(e, item.id)} className="absolute top-2 right-2 text-red-500 hover:text-red-300">✖</button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
