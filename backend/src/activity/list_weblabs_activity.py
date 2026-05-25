import azure.functions as func

from helper import app, handle_request, json_response, service


@app.route(route="weblabs", methods=["GET"])
def list_weblabs(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(lambda: json_response({"items": service.list_weblabs()}))
