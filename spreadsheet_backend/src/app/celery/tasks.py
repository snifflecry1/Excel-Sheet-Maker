from app.celery.celery import celery_app
from app.db_client.db_client import DBClient
from sqlalchemy.orm import sessionmaker
from app.redis_client.red_client import RedisClient
from sqlalchemy import create_engine
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:test@db:5432/test")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
redis_client = RedisClient()

@celery_app.task
def update_cell_task(spreadsheet_id, row_index, col_index, value, formula=None, references=None):
    session = Session()
    db_client = DBClient(session)
    try:
        response = db_client.update_cell(spreadsheet_id, row_index, col_index, value, formula)
        if response['success']:
            logger.info(f"Updated cell ({row_index}, {col_index}) for spreadsheet {spreadsheet_id} in DB")
        else:
            logger.error(f"Failed to update cell ({row_index}, {col_index}) for spreadsheet {spreadsheet_id} in DB: {response['error_type']}")
    except Exception as e:
        logger.exception(f"Error in update_cell_task: {e}")
        session.rollback()
    finally:
        session.close()
    return True

@celery_app.task
def export_spreadsheet_task(spreadsheet_id):
    session = Session()
    db_client = DBClient(session)
    try:
        spreadsheet = db_client.get_spreadsheet(spreadsheet_id)
        if not spreadsheet['success']:
            logger.error(f"Failed to retrieve spreadsheet {spreadsheet_id} for export: {spreadsheet['error_type']}")
            return None
        sheet = spreadsheet['data']['sheet']
        csv_output = sheet.export_to_csv()
        csv_path = f"/exports/spreadsheet_{spreadsheet_id}.csv"
        with open(csv_path, "w", newline='') as csvfile:
            csvfile.write(csv_output)
        logger.info(f"Exported spreadsheet {spreadsheet_id} to {csv_path}")
        return csv_path
    except Exception as e:
        logger.exception(f"Error in export_spreadsheet_task: {e}")
        return None
    finally:
        session.close()


# def validate_formula_helper(spreadsheet_id ,references, client_value, session) -> tuple[float, bool]:
#     db_client = DBClient(session)
#     total = 0.0
#     for ref in references:
#         row, col = ref
#         redis_key = f"spreadsheet:{spreadsheet_id}:cell:{row}:{col}"
#         cached = redis_client.get_redis_client().hget(redis_key, "value")
#         stored_cell_value = None
#         if cached is None:
#             response = db_client.get_cell(spreadsheet_id, row, col)
#             if response["success"]:
#                 data = response["data"]
#                 stored_cell_value = data.get('value')
#             else:
#                 return (0.0, False)
#         else:
#             stored_cell_value = cached.decode() if isinstance(cached, bytes) else cached
#         try:
#             total += float(stored_cell_value or 0)
#         except ValueError:
#             return (0, False)
#     return (total, abs(total - client_value) < 1e-9)
    