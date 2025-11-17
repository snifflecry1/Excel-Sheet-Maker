import React, { useEffect, useState, useCallback } from "react";
import { useSpreadsheetSocket } from "./useSpreadsheetSocket";
import { fetchSpreadsheetCells, exportSpreadsheet } from "./api";

export default function SpreadsheetView({ spreadsheet }) {
  const [cells, setCells] = useState([]);
  const [selectedCell, setSelectedCell] = useState(null);
  const [formula, setFormula] = useState("");
  const [value, setValue] = useState("");
  const [hasChanged, setHasChanged] = useState(false);
  const [formulaChanged, setFormulaChanged] = useState(false);

  // ✅ Load cells when spreadsheet changes
  useEffect(() => {
    if (spreadsheet?.id) {
      fetchSpreadsheetCells(spreadsheet.id).then((data) => {
        setCells(data.cells);
        setSelectedCell(null);
        setFormula("");
        setValue("");
      });
    }
  }, [spreadsheet]);

  // ✅ Handle backend updates (WebSocket)
  const handleBackendUpdate = useCallback(
    (update) => {
      if (!update || update.row === undefined || update.col === undefined) {
        console.warn("⚠️ Skipping invalid update:", update);
        return;
      }

      console.log("📡 Received update:", update);
      setCells((prev) =>
        prev.map((cell) =>
          cell.row_index === update.row && cell.col_index === update.col
            ? { ...cell, value: update.value, formula: update.formula }
            : cell
        )
      );

      if (
        selectedCell &&
        selectedCell.row === update.row &&
        selectedCell.col === update.col
      ) {
        setValue(update.value);
        setFormula(update.formula);
      }
    },
    [selectedCell]
  );

  // ✅ Connect socket
  const socket = useSpreadsheetSocket(handleBackendUpdate);

  // ✅ Emit to backend
  const emitCellUpdate = (update) => {
    if (socket && spreadsheet?.id) {
      console.log("🚀 Emitting sheet_updates:", update);
      socket.emit("sheet_updates", {
        spreadsheet_id: spreadsheet.id,
        update,
      });
    }
  };

  // ✅ Handle formula commit
  const handleFormulaCommit = () => {
    if (!selectedCell || !formulaChanged) return;

    const update = {
      row: selectedCell.row,
      col: selectedCell.col,
      value,
      formula,
    };

    emitCellUpdate(update);

    // ✅ Update local immediately
    setCells((prev) =>
      prev.map((cell) =>
        cell.row_index === selectedCell.row &&
        cell.col_index === selectedCell.col
          ? { ...cell, formula, value }
          : cell
      )
    );

    setFormulaChanged(false);
  };

  // ✅ Handle cell click
  const handleCellClick = (row, col) => {
    const cell = cells.find(
      (c) => c.row_index === row && c.col_index === col
    );
    setSelectedCell({ row, col });
    setFormula(cell?.formula || "");
    setValue(cell?.value || "");
  };

  // ✅ Export CSV
  const handleExport = async () => {
    const res = await exportSpreadsheet(spreadsheet.id);
    alert(res.message);
  };

  // ✅ Dynamically calculate grid size
  const numRows = cells.length
    ? Math.max(...cells.map((c) => c.row_index)) + 1
    : 10;

  const numCols = cells.length
    ? Math.max(...cells.map((c) => c.col_index)) + 1
    : 10;

  // ✅ Excel-style column naming (A → Z, AA, AB, etc.)
  function getColumnName(index) {
    let name = "";
    while (index >= 0) {
      name = String.fromCharCode((index % 26) + 65) + name;
      index = Math.floor(index / 26) - 1;
    }
    return name;
  }

  return (
    <div className="flex flex-col flex-grow p-4 h-full">
      {/* --- Top Bar --- */}
      <div className="flex items-center mb-4 gap-2">
        <input
          type="text"
          placeholder="Formula"
          value={formula}
          onChange={(e) => {
            setFormula(e.target.value);
            setFormulaChanged(true);
          }}
          onBlur={handleFormulaCommit}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleFormulaCommit();
          }}
          className="flex-1 border p-2 rounded"
        />
        <input
          type="text"
          placeholder="Value"
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setHasChanged(true);
          }}
          disabled={formula.startsWith("=")}
          className={`w-32 border p-2 rounded ${
            formula.startsWith("=") ? "bg-gray-100 text-gray-500" : ""
          }`}
        />
        <button
          onClick={handleExport}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Export CSV
        </button>
      </div>

      {/* --- Grid --- */}
      <div className="overflow-auto bg-white h-full">
        <table className="border-collapse w-full text-sm">
          <thead>
            <tr>
              <th className="w-8 bg-gray-200"></th>
              {Array.from({ length: numCols }, (_, i) => (
                <th
                  key={i}
                  className="border border-gray-300 bg-gray-100 text-center font-bold w-20 h-8"
                >
                  {getColumnName(i)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: numRows }, (_, r) => (
              <tr key={r}>
                <td className="border border-gray-300 bg-gray-100 text-center font-semibold w-8">
                  {r + 1}
                </td>
                {Array.from({ length: numCols }, (_, c) => {
                  const cell = cells.find(
                    (cl) => cl.row_index === r && cl.col_index === c
                  );
                  const isSelected =
                    selectedCell?.row === r && selectedCell?.col === c;

                  return (
                    <td
                      key={c}
                      onClick={() => handleCellClick(r, c)}
                      className="border border-gray-300 text-center w-[80px] h-[28px] p-0"
                    >
                      <input
                        type="text"
                        value={isSelected ? value : cell?.value || ""}
                        readOnly={!isSelected}
                        onFocus={() => setSelectedCell({ row: r, col: c })}
                        onChange={(e) => {
                          setValue(e.target.value);
                          setHasChanged(true);
                        }}
                        onBlur={() => {
                          if (hasChanged) {
                            const update = {
                              row: r,
                              col: c,
                              value,
                              formula,
                            };

                            emitCellUpdate(update);

                            // ✅ Instantly reflect change locally
                            setCells((prev) =>
                              prev.map((cell) =>
                                cell.row_index === r &&
                                cell.col_index === c
                                  ? { ...cell, value, formula }
                                  : cell
                              )
                            );

                            setHasChanged(false);
                          }
                        }}
                        className="w-full h-full text-center bg-transparent focus:outline-none border-none"
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
