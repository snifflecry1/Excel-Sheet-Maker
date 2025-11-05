from app import db
from app.models import SpreadsheetModel, SpreadsheetCell
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.spreadsheet.sheet import Spreadsheet
import logging
from mappings import ErrorCodes

logger = logging.getLogger(__name__)


class DBClient:
    def __init__(self, session):
        self.session = session
    def create_spreadsheet(self, name) -> dict:
        response = {"success": False, "error_type": None}
        try:
            sheet_model = SpreadsheetModel(name=name)
            self.session.add(sheet_model)
            self.session.flush()
            spreadsheet = Spreadsheet.from_db(self.session, sheet_model.id)
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
            self.session.commit()
            response["success"] = True
        except IntegrityError:
            logger.exception("Integrity error creating spreadsheet")
            db.session.rollback()
            response["error_type"] = ErrorCodes.INTEGRITY_ERROR
        except SQLAlchemyError as e:
            logger.exception(f"Database error creating sheet: {e}")
            db.session.rollback()
            response["error_type"] = ErrorCodes.ALCHEMY_ERROR
        except Exception as e:
            logger.exception("Unexpected error creating spreadsheet")
            db.session.rollback()
            response["error_type"] = ErrorCodes.GENERIC_ERROR
        return response
    
    def get_spreadsheet_cells(self, id):
        response = {"success": False, "error_type": None, "data": None}
        try:
            spreadsheet = Spreadsheet.from_db(self.session, id)
            cells = spreadsheet.get_cells()
            cells_data = [cell.to_dict() for cell in cells]
            response["success"] = True
            response["data"] = {"spreadsheet_id": spreadsheet.id, "cells": cells_data}
        except SpreadsheetModel.DoesNotExist:
            logger.exception("Spreadsheet not found")
            response["error_type"] = ErrorCodes.DOES_NOT_EXIST
        except SQLAlchemyError as e:
            logger.exception(f"Database error retrieving cells: {e}")
            response["error_type"] = ErrorCodes.ALCHEMY_ERROR
        return response