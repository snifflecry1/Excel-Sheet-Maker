import csv
import io
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from app.models import SpreadsheetCell, SpreadsheetModel
from app.spreadsheet.helpers import col_to_label, label_to_col, parse_formula
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class Spreadsheet:
    id: int
    name: str
    db: Session
    rows: int = 40
    cols: int = 40
    # This should be a dictionary for faster lookup
    cells: Dict[Tuple[int, int], SpreadsheetCell] = field(default_factory=dict)

    # total = 0
    # for ref in references:
    #     col_label = ''.join(filter(str.isalpha, ref))
    #     row_number = ''.join(filter(str.isdigit, ref))
    #     col_index = label_to_col(col_label)
    #     row_index = int(row_number) - 1  # Convert to 0-based index
    #     cell = next((c for c in cls.cells if c.row_index == row_index and c.col_index == col_index), None)
    #     if cell and cell.value and cell.value.isdigit():
    #         total += int(cell.value)
    # return str(total)

    @classmethod
    def from_db(cls, db, sheet_id: int) -> "Spreadsheet":
        meta = db.query(SpreadsheetModel).get(sheet_id)
        if not meta:
            raise ValueError(f"Spreadsheet with id {sheet_id} not found")
        cell_rows = (
            db.query(SpreadsheetCell)
            .filter_by(spreadsheet_id=sheet_id)
            .order_by(SpreadsheetCell.row_index, SpreadsheetCell.col_index)
            .all()
        )
        cell_map = {(c.row_index, c.col_index): c for c in cell_rows}
        return cls(id=meta.id, name=meta.name, db=db, cells=cell_map)

    # def get_cells(self, limit: int = 1000) -> List[SpreadsheetCell]:
    #     return (
    #         self.db.query(SpreadsheetCell)
    #         .filter_by(id = self.id)
    #         .order_by(SpreadsheetCell.row_index, SpreadsheetCell.col_index)
    #         .limit(limit)
    #         .all()
    #     )

    def update_cell_value(
        self, row_index: int, col_index: int, value: str, formula: str
    ) -> bool:
        if (row_index, col_index) in self.cells:
            cell = self.cells[(row_index, col_index)]
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
        max_row = max(c.row_index for c in self.cells.values())
        max_col = max(c.col_index for c in self.cells.values())

        # Build lookup table
        grid = [["" for _ in range(max_col + 1)] for _ in range(max_row + 1)]
        for (r, c), cell in self.cells.items():
            grid[r][c] = cell.value if cell.value is not None else ""

        # Write to CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(grid)
        return output.getvalue()

    def evaluate_formula(self, formula: str) -> str:
        tokens = parse_formula(formula)
        total = 0
        if not tokens:
            return "0"

        def get_cell_value(ref: str) -> str:
            col_label = "".join(filter(str.isalpha, ref))
            row_number = "".join(filter(str.isdigit, ref))
            col_index = label_to_col(col_label)
            row_index = int(row_number) - 1  # Convert to 0-based index
            cell = self.cells.get((row_index, col_index))
            return cell.value if (cell and cell.value and cell.value.isdigit()) else "0"

        total += int(get_cell_value(tokens[0]))
        i = 1
        while i < len(tokens):
            operator = tokens[i]
            operand = tokens[i + 1]
            logger.info(f"Processing token: {operator} {operand}")
            cell_value_str = get_cell_value(operand)
            cell_value = int(cell_value_str) if cell_value_str else 0
            logger.info(f"Evaluating: {operator} {operand} (value: {cell_value})")
            if operator == "+":
                total += cell_value
                logger.info(f"Total after addition: {total}")
            elif operator == "-":
                total -= cell_value
                logger.info(f"Total after subtraction: {total}")
            i += 2
        return str(total)
