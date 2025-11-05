from app.spreadsheet.sheet import Spreadsheet
from flask import Blueprint, request, jsonify, current_app
import logging
from mappings import ErrorCodes

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
    result = current_app.db_client.create_spreadsheet(name)
    if result["success"]:
        return jsonify({"message": "Spreadsheet created successfully"}), 201
    else:
        return jsonify({"message": f"Failed to create spreadsheet"}, result.get("error_type", 500))

@main_bp.route("/spreadsheets/<int:id>/cells", methods=["GET"])
def get_spreadsheet_cells(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    result = current_app.db_client.get_spreadsheet_cells(id)
    if result["success"]:
        return jsonify(result["data"]), 200
    else:
        return jsonify({"message": f"Failed to retrieve cells"}, result.get("error_type", 500))
