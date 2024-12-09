from rest_framework.renderers import JSONRenderer
from rest_framework.utils import json


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        custom_msg=None
        if "message" in data:
            custom_msg = data["message"]
            del data["message"]

        status_code = renderer_context['response'].status_code
        response = {
          "status": "success",
          "code": status_code,
          "data": data,
          "message": custom_msg
        }

        if not str(status_code).startswith('2'):
            response["status"] = "error"
            response["data"] = None
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["data"] = data

        # Handle exceptions
        if status_code == 500:
            response["status"] = "error"
            response["data"] = None
            response["message"] = "Internal server error"

        return super(ApiRenderer, self).render(response, accepted_media_type, renderer_context)
