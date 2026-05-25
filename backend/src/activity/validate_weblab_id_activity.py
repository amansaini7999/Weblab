import azure.functions as func

from helper import app, handle_request, json_response, read_json, service


@app.route(route="weblabs/validate-id", methods=["POST"])
def validate_weblab_id(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(lambda: json_response(service.validate_weblab_id(read_json(req))))
