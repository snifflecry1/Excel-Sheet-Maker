import json
from flask_socketio import emit
from app import socket
import redis
import logging

logger = logging.getLogger(__name__)
redis_client = None

r = redis.Redis(host="redis", port=6379, decode_responses=True)

@socket.on("connect")
def handle_connect():
    logger.info("Client connected")
    emit("connection_ack", {"message": "Connected to spreadsheet backend"})

@socket.on("disconnect")
def handle_disconnect():
    logger.info("Client disconnected")

@socket.on("cell_update")
def updates(data):
    try:
        spreadsheet_id = data.get('spreadsheet_id')
        update = data.get('update')
        if not spreadsheet_id or not update:
            emit("error", {"error": "Invalid payload"})
            return
        payload = json.dumps({"spreadsheet_id": spreadsheet_id, "update": update})
        r.publish('cell_updates', payload)
        emit("update_ack", {"status": "Update published", "spreadsheet_id": spreadsheet_id})
        logger.info(f"Published update to Redis: {payload}")
    except Exception as e:
        logger.exception("Error handling cell_update")
        emit("error", {"error": "Internal server error"})
