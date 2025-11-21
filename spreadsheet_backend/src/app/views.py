import logging
import os

from app.celery.tasks import export_spreadsheet_task
from app.spreadsheet.sheet import Spreadsheet
from flask import Blueprint, current_app, jsonify, request, send_file
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
        return (
            jsonify({"error": "Spreadsheet name is required and must be a string"}),
            400,
        )
    if len(name) > 255:
        return (
            jsonify({"error": "Spreadsheet name must not exceed 255 characters"}),
            400,
        )
    result = current_app.db_client.create_spreadsheet(name)
    if result["success"]:
        return (
            jsonify({"message": "Spreadsheet created successfully", "data": result}),
            201,
        )
    else:
        return jsonify(
            {"message": f"Failed to create spreadsheet"}, result.get("error_type", 500)
        )


@main_bp.route("/spreadsheets/<int:id>", methods=["GET"])
def get_spreadsheet(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    if id in current_app.sheet_registry:
        cached_sheet = current_app.sheet_registry[id]
        # return jsonify({"spreadsheet_id": id, "sheet": cached_sheet}), 200
    else:
        result = current_app.db_client.get_spreadsheet(id)
        if result["success"]:
            cached_sheet = result["data"]["sheet"]
            current_app.sheet_registry[id] = cached_sheet
        else:
            return jsonify(
                {"message": f"Failed to retrieve cells"}, result.get("error_type", 500)
            )
    sheet_data = {
        "id": cached_sheet.id,
        "name": cached_sheet.name,
        "rows": cached_sheet.rows,
        "cols": cached_sheet.cols,
        "cells": [
            {
                "row_index": r,
                "col_index": c,
                "value": cell.value,
                "formula": cell.formula,
            }
            for (r, c), cell in cached_sheet.cells.items()
        ],
    }
    return (
        jsonify(
            {
                "message": "Retrieved sheet data",
                "spreadsheet_id": id,
                "sheet": sheet_data,
            }
        ),
        200,
    )


@main_bp.route("/spreadsheets/export_csv/<int:id>", methods=["GET"])
def export_spreadsheet_csv(id):
    path = f"/exports/spreadsheet_{id}.csv"
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400
    try:
        export_spreadsheet_task.delay(id)  # type: ignore
        return send_file(
            path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"spreadsheet_{id}.csv",
        )
    except ValueError as ve:
        logger.error(f"Export error: {ve}")
        return jsonify({"error": str(ve)}), 404
    except Exception as e:
        logger.exception(f"Unexpected error during export: {e}")
        return jsonify({"error": "Internal server error"}), 500


@main_bp.route("/spreadsheets/export_csv/<int:id>/start", methods=["POST"])
def start_export_spreadsheet(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400

    async_result = export_spreadsheet_task.delay(id)  # type: ignore

    return jsonify({"job_id": async_result.id, "spreadsheet_id": id}), 202


@main_bp.route("/spreadsheets/export_csv/<int:id>/status", methods=["GET"])
def export_spreadsheet_status(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400

    csv_path = f"/exports/spreadsheet_{id}.csv"
    exists = os.path.exists(csv_path)
    current_app.logger.info(f"[STATUS] Check {csv_path}, exists={exists}")
    if os.path.exists(csv_path):
        return jsonify({"ready": True}), 200

    return jsonify({"ready": False}), 202


@main_bp.route("/spreadsheets/export_csv/<int:id>/download", methods=["GET"])
def download_spreadsheet_csv(id):
    if id <= 0:
        return jsonify({"error": "Invalid spreadsheet ID"}), 400

    csv_path = f"/exports/spreadsheet_{id}.csv"
    exists = os.path.exists(csv_path)
    current_app.logger.info(f"[DOWNLOAD] {csv_path} exists={exists}")
    if not os.path.exists(csv_path):
        return jsonify({"error": "Export not ready"}), 404

    try:
        return send_file(
            csv_path,
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"spreadsheet_{id}.csv",
        )
    except Exception as e:
        logger.exception(f"Error sending CSV for spreadsheet {id}: {e}")
        return jsonify({"error": "Internal server error"}), 500
