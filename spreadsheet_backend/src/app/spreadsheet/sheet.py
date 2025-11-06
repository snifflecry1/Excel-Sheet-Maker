from typing import List
from dataclasses import dataclass
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
    
    
    @classmethod
    def from_db(cls, db, sheet_id: int) -> "Spreadsheet":
        meta = db.query(SpreadsheetModel).get(sheet_id)
        if not meta:
            raise ValueError(f"Spreadsheet with id {sheet_id} not found")
        return cls(id=meta.id, name=meta.name, db=db)
    
    def get_cells(self, limit: int = 1000) -> List[SpreadsheetCell]:
        return (
            self.db.query(SpreadsheetCell)
            .filter_by(id = self.id)
            .order_by(SpreadsheetCell.row_index, SpreadsheetCell.col_index)
            .limit(limit)
            .all()
        )
    
    def update_cell_value(self, row_index: int, col_index: int, value: str) -> bool:
        cell = (
            self.db.query(SpreadsheetCell)
            .filter_by(spreadsheet_id=self.id, row_index=row_index, col_index=col_index)
            .first()
        )
        if not cell:
            return False
        cell.value = value
        return True
    

    # def export_to_csv(self, path):
    #     implement later
        
    

        