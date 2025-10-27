from app.spreadsheet.sheet import Spreadsheet
from flask import Blueprint, request, jsonify
import logging
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app import db
from app.models import SpreadsheetModel, SpreadsheetCell

logger = logging.getLogger(__name__)
main_bp = Blueprint("main", __name__)

@main_bp.route("/spreadsheets", methods=["POST"])
def create_spreadsheet():
    if not request.is_json:
        return jsonify({"error": "Invalid input, JSON expected"}), 400
    data = request.get_json()
    name = data.get("name")
    if not name or not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Spreadsheet name is required and must be a string"}), 400
    if len(name) > 255:
        return jsonify({"error": "Spreadsheet name must not exceed 255 characters"}), 400
    
    try:     
        sheet_model = SpreadsheetModel(name=name)
        db.session.add(sheet_model)
        db.session.flush()  
        spreadsheet = Spreadsheet.from_db(db.session, sheet_model.id)       
        for r in range(spreadsheet.rows):
            for c in range(spreadsheet.cols):
                sheet_model.cells.append(
                SpreadsheetCell(
                    row_index=r,
                    col_index=c,
                    value=None,
                    formula=None,
                )
        )

        db.session.commit()
        return jsonify({
            "id": sheet_model.id,
            "name": sheet_model.name,
            "rows": spreadsheet.rows,
            "cols": spreadsheet.cols,
            "created_at": sheet_model.created_at.isoformat(),
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Spreadsheet with this name already exists"}), 409
    except SQLAlchemyError as e:
        logger.exception(f"Database error creating sheet: {e}")
        db.session.rollback()
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.exception("Unexpected error creating spreadsheet")
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500

@main_bp.route("/spreadsheets/<int:id>/cells", methods=["GET"])
def get_spreadsheet_cells(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    try:
        spreadsheet = Spreadsheet.from_db(db.session, id)
        cells = spreadsheet.get_cells()
        cells_data = [cell.to_dict() for cell in cells]
        return jsonify({"spreadsheet_id": spreadsheet.id, "cells": cells_data}), 200
    except SpreadsheetModel.DoesNotExist:
        return jsonify({"error": "Spreadsheet not found"}), 404
    except SQLAlchemyError as e:
        logger.exception(f"Database error retrieving cells: {e}")
        return jsonify({"error": "Database error occurred"}), 500