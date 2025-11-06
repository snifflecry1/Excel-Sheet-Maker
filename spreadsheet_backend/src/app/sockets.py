import json
from flask_socketio import emit
from app import socket
from flask import current_app
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
        current_app.redis_client.update_cached_cell(
            spreadsheet_id,
            update.get('row'),
            update.get('col'),
            update.get('value')
        )
        logger.info(f"Updated cached cell for spreadsheet {spreadsheet_id}")
        current_app.redis_client.publish_update_task(spreadsheet_id, update.get('row'), update.get('col'), update.get('value'))
        logger.info(f"Added db update task for spreadsheet {spreadsheet_id}")
        emit("update_ack", {"status": "Update added to task queue", "spreadsheet_id": spreadsheet_id})
        logger.info(f"Published both updates to Redis")
    except Exception as e:
        logger.exception(f"Error handling cell_update: {e}")
        emit("error", {"error": "Internal server error"})
