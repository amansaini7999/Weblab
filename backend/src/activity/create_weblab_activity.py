import azure.functions as func

from helper import app, handle_request, json_response, read_json, service


@app.route(route="weblabs", methods=["POST"])
def create_weblab(req: func.HttpRequest) -> func.HttpResponse:
    return handle_request(lambda: json_response(service.create_weblab(read_json(req)), status_code=201))
