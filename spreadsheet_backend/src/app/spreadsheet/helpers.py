import re

# Helper functions for spreadsheet operations


def parse_formula(formula: str) -> list[str]:
    """
    Parse an Excel-style addition formula (e.g., '=A1+B2+C3') into a list of cell references.
    Returns ['A1', 'B2', 'C3'].
    """
    formula = formula.strip()
    if formula.startswith("="):
        formula = formula[1:]

    pattern = r"([A-Z]+[0-9]+|[+-])"

    matches = re.findall(pattern, formula.upper())
    return matches


def col_to_label(index: int) -> str:
    """Convert 0-based column index (0 -> 'A') to label."""
    label = ""
    while index >= 0:
        label = chr(index % 26 + ord("A")) + label
        index = index // 26 - 1
    return label


def label_to_col(label: str) -> int:
    """Convert label ('A' -> 0) back to 0-based index."""
    if not label:
        return -1
    index = 0
    for char in label.upper():
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1
