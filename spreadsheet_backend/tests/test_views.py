import json
from unittest.mock import MagicMock

import pytest
from app import create_app
from app.spreadsheet.sheet import Spreadsheet

# ---------- Fixtures ----------


@pytest.fixture
def app():
    # create_app returns (flask_app, socket)
    flask_app, _ = create_app()

    flask_app.config.update(
        TESTING=True,
    )

    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_db_client(app):
    """
    Attach a MagicMock as app.db_client so tests can control behavior.
    """
    mock = MagicMock()
    app.db_client = mock
    return mock


# ---------- Helper ----------


def _make_fake_sheet():
    """
    Minimal fake Spreadsheet compatible with your view logic.
    Adjust if your real Spreadsheet has a different signature.
    """
    sheet = Spreadsheet(
        name="TestSheet",
        id=3,
        db="test",
        rows=2,
        cols=2,
    )
    # Your view expects: cached_sheet.cells is a dict keyed by (r, c)
    sheet.cells = {
        (0, 0): MagicMock(value="A1", formula=None),
        (0, 1): MagicMock(value="B1", formula="=1+1"),
        (1, 0): MagicMock(value=None, formula=None),
        (1, 1): MagicMock(value="B2", formula=None),
    }
    sheet.id = 42
    return sheet


# ---------- Tests: POST /spreadsheets ----------


def test_create_spreadsheet_success(client, mock_db_client):
    mock_db_client.create_spreadsheet.return_value = {
        "success": True,
        "data": {
            "spreadsheet": {
                "id": 123,
                "name": "My Sheet",
            }
        },
        "error_type": None,
    }

    payload = {"name": "My Sheet"}
    resp = client.post(
        "/spreadsheets",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code == 201
    body = resp.get_json()
    assert body["message"] == "Spreadsheet created successfully"
    mock_db_client.create_spreadsheet.assert_called_once_with("My Sheet")


def test_create_spreadsheet_invalid_payload(client, mock_db_client):
    # No name
    resp = client.post(
        "/spreadsheets",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert "Spreadsheet name is required" in body["error"]

    # Empty string
    resp = client.post(
        "/spreadsheets",
        data=json.dumps({"name": "   "}),
        content_type="application/json",
    )
    assert resp.status_code == 400

    # Non-string
    resp = client.post(
        "/spreadsheets",
        data=json.dumps({"name": 123}),
        content_type="application/json",
    )
    assert resp.status_code == 400


# ---------- Tests: GET /spreadsheets ----------


def test_list_spreadsheets_success(client, mock_db_client):
    mock_db_client.list_spreadsheets.return_value = {
        "success": True,
        "data": {
            "spreadsheets": [
                {"id": 1, "name": "Sheet 1"},
                {"id": 2, "name": "Sheet 2"},
            ]
        },
        "error_type": None,
    }

    resp = client.get("/spreadsheets")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "spreadsheets" in body
    assert len(body["spreadsheets"]) == 2
    assert body["spreadsheets"][0]["name"] == "Sheet 1"
    mock_db_client.list_spreadsheets.assert_called_once()


# ---------- Tests: GET /spreadsheets/<id> ----------


def test_get_spreadsheet_success_from_db(client, mock_db_client):
    fake_sheet = _make_fake_sheet()

    mock_db_client.get_spreadsheet.return_value = {
        "success": True,
        "data": {"sheet": fake_sheet},
        "error_type": None,
    }

    resp = client.get("/spreadsheets/42")
    assert resp.status_code == 200
    body = resp.get_json()

    assert body["spreadsheet_id"] == 42
    sheet_data = body["sheet"]
    assert sheet_data["id"] == fake_sheet.id
    assert sheet_data["name"] == fake_sheet.name
    assert sheet_data["rows"] == fake_sheet.rows
    assert sheet_data["cols"] == fake_sheet.cols

    # Flattened cells list
    assert len(sheet_data["cells"]) == len(fake_sheet.cells)

    a1 = next(
        c for c in sheet_data["cells"] if c["row_index"] == 0 and c["col_index"] == 0
    )
    assert a1["value"] == "A1"


def test_get_spreadsheet_invalid_id(client):
    resp = client.get("/spreadsheets/0")
    assert resp.status_code == 400
    body = resp.get_json()
    assert "Invalid spreadsheet ID" in body["error"]


def test_get_spreadsheet_uses_cache(client, app, mock_db_client):
    fake_sheet = _make_fake_sheet()
    with app.app_context():
        app.sheet_registry[123] = fake_sheet

    resp = client.get("/spreadsheets/123")
    assert resp.status_code == 200
    body = resp.get_json()
    # From fake_sheet.id = 42
    assert body["sheet"]["id"] == 42
    # Should not call db_client.get_spreadsheet because cache hit
    mock_db_client.get_spreadsheet.assert_not_called()
