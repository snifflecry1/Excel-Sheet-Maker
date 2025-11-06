import redis
import os
import logging
from app.celery.tasks import update_cell_task

logger = logging.getLogger(__name__)
class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None

    def get_redis_client(self):
        if not self.redis_client:
            self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        return self.redis_client
    
    def publish_update_task(self, spreadsheet_id: str, row_index: int, col_index: int, value: str):
        try:
            return update_cell_task.delay( # type: ignore
                spreadsheet_id,
                row_index,
                col_index,
                value
            )
        except AttributeError as e:
            logger.error(f"Failed to publish update task: {e}")
            return None

    
    def cache_sheet_state(self, spreadsheet_id, cell_data):
        client = self.get_redis_client()
        key = f"spreadsheet:{spreadsheet_id}"
        pipe = client.pipeline(transaction=True)
        for cell in cell_data:
            cell_key = f"cell:{cell['row_index']}:{cell['col_index']}"
            pipe.hset(key, cell_key, cell['value'] if cell['value'] is not None else "")
        pipe.execute()
        logger.info(f"Cached state for spreadsheet {spreadsheet_id}")
        return True
    
    def get_cached_sheet_state(self, spreadsheet_id):
        client = self.get_redis_client()
        key = f"spreadsheet:{spreadsheet_id}"
        cell_data = client.hgetall(key)
        if not cell_data:
            return None
        cells = [
            {
                "row_index": int(k.split(":")[1]),
                "col_index": int(k.split(":")[2]),
                "value": v if v != "" else None
            }
            for k, v in cell_data.items()
        ]
        logger.info(f"Retrieved cached state for spreadsheet {spreadsheet_id}")
        return cells
    
    def update_cached_cell(self, spreadsheet_id, row_index, col_index, value):
        client = self.get_redis_client()
        key = f"spreadsheet:{spreadsheet_id}"
        cell_key = f"cell:{row_index}:{col_index}"
        client.hset(key, cell_key, value if value is not None else "")
        logger.info(f"Updated cached cell ({row_index}, {col_index}) for spreadsheet {spreadsheet_id}")
        return True
    
    def clear_cached_sheet(self, spreadsheet_id):
        client = self.get_redis_client()
        key = f"spreadsheet:{spreadsheet_id}"
        client.delete(key)
        logger.info(f"Cleared cached state for spreadsheet {spreadsheet_id}")
        return True

        
    