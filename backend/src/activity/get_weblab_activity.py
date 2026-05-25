import azure.functions as func

from helper import app, handle_request, json_response, service


@app.route(route="weblabs/{weblab_id}", methods=["GET"])
def get_weblab(req: func.HttpRequest) -> func.HttpResponse:
    weblab_id = req.route_params.get("weblab_id", "")
    return handle_request(lambda: json_response(service.get_weblab(weblab_id)))
