import azure.functions as func

from helper import app, handle_request, json_response, read_json, service


@app.route(route="weblabs/{weblab_id}/getTreatment", methods=["POST"])
def get_treatment(req: func.HttpRequest) -> func.HttpResponse:
    weblab_id = req.route_params.get("weblab_id", "")
    return handle_request(lambda: json_response(service.get_treatment(weblab_id, read_json(req))))