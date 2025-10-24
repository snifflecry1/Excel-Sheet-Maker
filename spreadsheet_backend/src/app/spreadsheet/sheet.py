class Spreadsheet:
    def __init__(self, name: str, rows: int, cols: int):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.cells = [[ '' for _ in range(self.cols)] for _ in range(self.rows)]
    
    def set_cell(self, row: int, col: int, value: str):
        self.cells[row][col] = value
    

        