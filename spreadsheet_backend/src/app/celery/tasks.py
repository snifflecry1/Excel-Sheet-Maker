from app.celery.celery import celery_app
from app.db_client.db_client import DBClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://test:test@db:5432/test")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

@celery_app.task
def update_cell_task(spreadsheet_id, row_index, col_index, value):
    session = Session()
    db_client = DBClient(session)
    try:
        db_client.update_cell(spreadsheet_id, row_index, col_index, value)
    finally:
        session.close()
    return True