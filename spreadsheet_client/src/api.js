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

// export async function exportSpreadsheet(id) {
//   const res = await fetch(`${BASE_URL}//spreadsheets/export_csv/${id}`);
//     if (!res.ok) throw new Error("Failed to download CSV");
//   const blob = res.blob();
//   const url = window.URL.createObjectURL(blob);
//   const a = document.createElement('link');
//   a.href = url;
//   a.download = `spreadsheet_${id}.csv`
//   document.body.appendChild(a);
//   a.click();
//   a.remove();
//   window.URL.revokeObjectURL(url);
//   return res.json();
// }

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

export async function startExportSpreadsheet(id) {
  const res = await fetch(`${BASE_URL}/spreadsheets/export_csv/${id}/start`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to start export");
  }

  return res.json();
}

export async function checkExportStatus(id) {
  const res = await fetch(`${BASE_URL}/spreadsheets/export_csv/${id}/status`);
  if (!res.ok && res.status !== 202) {
    throw new Error("Failed to check export status");
  }
  return res.json();
}

export async function downloadSpreadsheetCsv(id) {
  const res = await fetch(`${BASE_URL}/spreadsheets/export_csv/${id}/download`);
  if (!res.ok) {
    throw new Error("Failed to download CSV");
  }
  return res.blob();
}