import azure.functions as func

from helper import app, json_response


@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return json_response({"status": "ok", "service": "weblab-api"})
