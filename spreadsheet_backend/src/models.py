from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Cell:
    value: Optional[str] = None
    formula: list[Optional[str]] = []

@dataclass
class Spreadsheet:
    id: int
    name: str
    cells: List[List[Cell]]
    rows: int
    columns: int
