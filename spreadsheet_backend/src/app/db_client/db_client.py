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
    
    def get_spreadsheet(self, id):
        response = {"success": False, "error_type": None, "data": None}
        try:
            sheet = Spreadsheet.from_db(self.session, id)
            # cells = spreadsheet.cells
            # cells_data = [cell.to_dict() for cell in cells]
            response["success"] = True
            response["data"] = {"sheet": sheet}
        except SpreadsheetModel.DoesNotExist:
            logger.exception("Spreadsheet not found")
            response["error_type"] = ErrorCodes.DOES_NOT_EXIST
        except SQLAlchemyError as e:
            logger.exception(f"Database error retrieving sheet: {e}")
            response["error_type"] = ErrorCodes.ALCHEMY_ERROR
        return response
    
    def update_cell(self, spreadsheet_id, row_index, col_index, value) -> dict:
        response = {"success": False, "error_type": None}
        try:
            cell = (
                self.session.query(SpreadsheetCell)
                .filter_by(spreadsheet_id=spreadsheet_id, row_index=row_index, col_index=col_index)
                .first()
            )
            if cell:
                cell.value = value
            else:
                response["error_type"] = ErrorCodes.DOES_NOT_EXIST
                return response
            self.session.commit()
            response["success"] = True
        except ValueError as e:
            logger.exception("Spreadsheet not found for update")
            response["error_type"] = ErrorCodes.DOES_NOT_EXIST
        except SQLAlchemyError as e:
            logger.exception(f"Database error updating cell: {e}")
            self.session.rollback()
            response["error_type"] = ErrorCodes.ALCHEMY_ERROR
        except Exception as e:
            logger.exception("Unexpected error updating cell")
            self.session.rollback()
            response["error_type"] = ErrorCodes.GENERIC_ERROR
        return response
    
    
    def get_cell(self, spreadsheet_id, row_index, col_index) -> dict:
        response = {"success": False, "error_type": None, "data": None}
        try:
            cell_data = (
                self.session.query(SpreadsheetCell)
                .filter_by(spreadsheet_id=spreadsheet_id, row_index=row_index, col_index=col_index)
                .first()
            )
            if cell_data is None:
                response["error_type"] = ErrorCodes.DOES_NOT_EXIST
                return response
            response["success"] = True
            response["data"] = cell_data
        except SQLAlchemyError as e:
            logger.exception(f"Database error retrieving cell: {e}")
            response["error_type"] = ErrorCodes.ALCHEMY_ERROR
        return response