from typing import List, Optional
from app.extensions import db
from datetime import datetime, timezone

class SpreadsheetModel(db.Model):
    __tablename__ = "spreadsheets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    cells = db.relationship("SpreadsheetCell", back_populates="spreadsheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Spreadsheet id={self.id} name={self.name}>"

class SpreadsheetCell(db.Model):
    __tablename__ = "cells"

    id = db.Column(db.Integer, db.ForeignKey("spreadsheets.id"), primary_key=True)
    row_index = db.Column(db.Integer, primary_key=True)
    col_index = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Text, nullable=True)
    formula = db.Column(db.Text, nullable=True)
    spreadsheet = db.relationship("SpreadsheetModel", back_populates="cells")

    def __repr__(self):
        return f"<Cell spreadsheet_id={self.id} row={self.row_index} col={self.col_index} value={self.value}>"
    
    def to_dict(self) -> dict:
        return {
            "row_index": self.row_index,
            "col_index": self.col_index,
            "value": self.value,
            "formula": self.formula,
        }
