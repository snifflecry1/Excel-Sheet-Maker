from app.spreadsheet.sheet import Spreadsheet
from flask import current_app
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

@main_bp.route("/spreadsheets/<int:id>", methods=["GET"])
def get_spreadsheet(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    if id in current_app.sheet_registry:
        cached_sheet = current_app.sheet_registry[id]
        return jsonify({"spreadsheet_id": id, "sheet": cached_sheet}), 200
    result = current_app.db_client.get_spreadsheet(id)
    if result["success"]:
        sheet = result["data"]["sheet"]
        current_app.sheet_registry[id] = (sheet)
        return jsonify({"message": "Retrieved sheet data" , "spreadsheet_id": sheet.id, "name": sheet.name, "sheet": sheet}), 200
    else:
        return jsonify({"message": f"Failed to retrieve cells"}, result.get("error_type", 500))

@main_bp.route("/spreadsheets/export_csv/<int:id>", methods=["GET"])
def export_spreadsheet_csv(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    try:
        spreadsheet = Spreadsheet.from_db(current_app.db_client.session, id)
        csv_path = f"/tmp/spreadsheet_{id}.csv"
        output  = spreadsheet.export_to_csv()  # Uncomment when implemented
        with open(csv_path, "w", newline='') as csvfile:
            csvfile.write(output)
        return jsonify({"message": f"Spreadsheet exported to {csv_path}"}), 200
    except ValueError as ve:
        logger.error(f"Export error: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.exception(f"Unexpected error during export: {e}")
        return jsonify({"error": "Internal server error"}), 500
