import json
from flask_socketio import emit
from app import socket
from flask import current_app
from app.spreadsheet.sheet import Spreadsheet
from app.celery.tasks import update_cell_task
import logging

logger = logging.getLogger(__name__)
redis_client = None

@socket.on("connect")
def handle_connect():
    logger.info("Client connected")
    emit("connection_ack", {"message": "Connected to spreadsheet backend"})

@socket.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")

@socket.on("sheet_updates")
def updates(data):
    try:
        spreadsheet_id = data.get('spreadsheet_id')
        update = data.get('update')
        if not spreadsheet_id or not update:
            emit("error", {"error": "Invalid payload"})
            return
        row = update.get("row")
        col = update.get("col")
        value = update.get("value")
        formula = update.get("formula")
        registry = current_app.sheet_registry
        if spreadsheet_id in registry:
            sheet = registry[spreadsheet_id]
        else:
            db = current_app.db_client
            sheet = db.get_spreadsheet(spreadsheet_id)["data"]["sheet"]
            registry[spreadsheet_id] = sheet
            logger.info(f"📘 Loaded sheet {spreadsheet_id} into memory")
        updated = sheet.update_cell_value(row, col, value, formula)

            # for cell in cells:
            #     if cell['row_index'] == update.get('row') and cell['col_index'] == update.get('col'):
            #         cell['value'] = update.get('value')
            #         break
            # current_app.sheet_registry[spreadsheet_id] = (name, cells)
            # logger.info(f"Updated in-memory cache for spreadsheet {spreadsheet_id}")
        try:
            # UPDATE THIS TASK METHOD 
            update_cell_task.delay( # type: ignore
                spreadsheet_id,
                update.get('row'),
                update.get('col'), 
                update.get('value'),
                update.get('formula'),
                # update.get('references')
            )
        except AttributeError as e:
            logger.error(f"Failed to publish update task: {e}")
            return None
        logger.info(f"Added db update task for spreadsheet {spreadsheet_id}")
        emit("update_ack", {"status": "Update added to task queue", "spreadsheet_id": spreadsheet_id})
        logger.info(f"Published both updates to Redis")
    except Exception as e:
        logger.exception(f"Error handling cell_update: {e}")
        emit("error", {"error": "Internal server error"})
