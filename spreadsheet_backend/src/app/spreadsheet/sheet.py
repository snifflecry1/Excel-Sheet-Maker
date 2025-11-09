import csv
import io
from typing import List
from dataclasses import dataclass, field
from app.models import SpreadsheetModel, SpreadsheetCell
from app import db
from sqlalchemy.orm import Session

@dataclass
class Spreadsheet:
    id: int
    name: str
    db: Session
    rows: int = 40
    cols: int  = 40
    cells: List[SpreadsheetCell] = field(default_factory=list)
    
    
    @classmethod
    def from_db(cls, db, sheet_id: int) -> "Spreadsheet":
        meta = db.query(SpreadsheetModel).get(sheet_id)
        if not meta:
            raise ValueError(f"Spreadsheet with id {sheet_id} not found")
        cells = (
            db.query(SpreadsheetCell)
            .filter_by(spreadsheet_id=sheet_id)
            .order_by(SpreadsheetCell.row_index, SpreadsheetCell.col_index)
            .all()
        )
        return cls(id=meta.id, name=meta.name, db=db, cells=cells)
    
    # def get_cells(self, limit: int = 1000) -> List[SpreadsheetCell]:
    #     return (
    #         self.db.query(SpreadsheetCell)
    #         .filter_by(id = self.id)
    #         .order_by(SpreadsheetCell.row_index, SpreadsheetCell.col_index)
    #         .limit(limit)
    #         .all()
    #     )
    
    def update_cell_value(self, row_index: int, col_index: int, value: str, formula: str) -> bool:
        for cell in self.cells:
            if cell.row_index == row_index and cell.col_index == col_index:
                cell.value = value
                cell.formula = formula
                return True
        return False
        # cell = (
        #     self.db.query(SpreadsheetCell)
        #     .filter_by(spreadsheet_id=self.id, row_index=row_index, col_index=col_index)
        #     .first()
        # )
        # if not cell:
        #     return False
        # cell.value = value
        # return True
    

    def export_to_csv(self) -> str:
        """Export current in-memory sheet to CSV string."""
        if not self.cells:
            return ""
        
        # Find sheet bounds
        max_row = max(c.row_index for c in self.cells)
        max_col = max(c.col_index for c in self.cells)

        # Build lookup table
        grid = [[ "" for _ in range(max_col + 1)] for _ in range(max_row + 1)]
        for c in self.cells:
            grid[c.row_index][c.col_index] = c.value or ""

        # Write to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(grid)
        return output.getvalue()
        
    

        