const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";
export async function fetchSpreadsheets() {
  const res = await fetch(`${BASE_URL}/spreadsheets`);
  const data = await res.json();
  return data.spreadsheets; 
}

export async function fetchSpreadsheetCells(id) {
  const res = await fetch(`${BASE_URL}//spreadsheets/${id}`);
  const data = await res.json();
  return data.sheet;
}

export async function exportSpreadsheet(id) {
  const res = await fetch(`${BASE_URL}//spreadsheets/export_csv/${id}`);
  return res.json();
}

export async function createSpreadsheet(name) {
  const res = await fetch(`${BASE_URL}/spreadsheets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });

  if (!res.ok) {
    throw new Error("Failed to create spreadsheet");
  }

  const result = await res.json();
  return result.data; // contains { success, spreadsheet, ... }
}
