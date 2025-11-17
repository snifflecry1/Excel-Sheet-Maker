import React, { useEffect, useState } from "react";
import SpreadsheetView from "./SpreadsheetView";
import { fetchSpreadsheets, createSpreadsheet } from "./api";

export default function App() {
  const [spreadsheets, setSpreadsheets] = useState([]);
  const [selectedSheet, setSelectedSheet] = useState(null);
  const [isCreating, setIsCreating] = useState(false);
  const [newSheetName, setNewSheetName] = useState("");

  // ✅ Load all spreadsheets on startup
  useEffect(() => {
    fetchSpreadsheets()
      .then((data) => setSpreadsheets(data))
      .catch((err) => console.error("Failed to load spreadsheets:", err));
  }, []);

  // ✅ Create new sheet (don’t auto-select)
  const handleCreateSheet = async () => {
    if (!newSheetName.trim()) return;

    try {
      const res = await createSpreadsheet(newSheetName.trim());
      // Add new sheet to sidebar list
      setSpreadsheets((prev) => [...prev, res.spreadsheet]);
      // Reset input state
      setNewSheetName("");
      setIsCreating(false);
    } catch (err) {
      console.error("Failed to create spreadsheet:", err);
      alert("Error creating spreadsheet");
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* --- Sidebar --- */}
      <aside className="w-64 bg-white border-r p-4 flex flex-col">
        <h1 className="text-xl font-bold mb-4">Spreadsheets</h1>

        {/* List of available spreadsheets */}
        <div className="flex flex-col gap-1 overflow-auto flex-grow">
          {console.log("📊 Spreadsheets in state:", spreadsheets)}
          {spreadsheets.map((sheet) => (
            <button
              key={sheet.id}
              onClick={() => setSelectedSheet(sheet)}
              className={`text-left px-3 py-2 rounded hover:bg-green-100 ${
                selectedSheet?.id === sheet.id ? "bg-green-200 font-semibold" : ""
              }`}
            >
              {sheet.name}
            </button>
          ))}
        </div>

        {/* --- Create New Spreadsheet --- */}
        <div className="mt-4">
          {isCreating ? (
            <input
              type="text"
              placeholder="New sheet name..."
              value={newSheetName}
              onChange={(e) => setNewSheetName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleCreateSheet();
                if (e.key === "Escape") {
                  setIsCreating(false);
                  setNewSheetName("");
                }
              }}
              autoFocus
              className="w-full border rounded p-2 focus:outline-none focus:ring focus:ring-green-300"
            />
          ) : (
            <button
              onClick={() => setIsCreating(true)}
              className="w-full flex items-center justify-center border border-dashed border-gray-400 p-2 rounded hover:bg-gray-50 text-gray-600"
            >
              <span className="text-lg font-bold mr-1">+</span> New Spreadsheet
            </button>
          )}
        </div>
      </aside>

      {/* --- Main Content --- */}
      <main className="flex-1 flex flex-col">
        {selectedSheet ? (
          <SpreadsheetView spreadsheet={selectedSheet} />
        ) : (
          <div className="flex items-center justify-center text-gray-500">
            Select a spreadsheet to view or create a new one
          </div>
        )}
      </main>
    </div>
  );
}
