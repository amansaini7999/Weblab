import azure.functions as func

from helper import app, handle_request, json_response, read_json, service


@app.route(route="weblabs/{weblab_id}/allocation", methods=["PUT"])
def update_allocation(req: func.HttpRequest) -> func.HttpResponse:
    weblab_id = req.route_params.get("weblab_id", "")
    return handle_request(lambda: json_response(service.update_allocation(weblab_id, read_json(req))))
