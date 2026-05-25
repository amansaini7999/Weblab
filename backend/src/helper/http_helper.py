import json
from typing import Any, Callable, Dict

import azure.functions as func

from errors import NotFoundError, ValidationError
from repositories import build_repository
from services import WeblabService

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
service = WeblabService(build_repository())


def json_response(payload: Dict[str, Any], status_code: int = 200) -> func.HttpResponse:
    return func.HttpResponse(body=json.dumps(payload), status_code=status_code, mimetype="application/json")


def read_json(req: func.HttpRequest) -> Dict[str, Any]:
    try:
        data = req.get_json()
        if isinstance(data, dict):
            return data
        raise ValueError("request body must be a JSON object")
    except ValueError as exc:
        raise ValidationError([str(exc)]) from exc


def handle_request(callback: Callable[[], func.HttpResponse]) -> func.HttpResponse:
    try:
        return callback()
    except NotFoundError as exc:
        return json_response({"error": str(exc)}, status_code=404)
    except ValidationError as exc:
        return json_response({"error": "validation_error", "details": exc.errors}, status_code=400)
