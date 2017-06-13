from httplib import HTTPResponse
from api_exceptions import APIException
import json


class APIResponse:
    def __repr__(self):
        return "mgmt_api_lib::APIResponse\n" + json.dumps(self.as_dict(), indent=4, sort_keys=True)

    def __init__(self, json_response, success, status_code=None, err_message=""):
        if err_message:
            self.success = False
            self.error_message = err_message
            self.res_obj = {}
        else:
            self.status_code = status_code
            self.success = success
            try:
                data_dict = json.loads(json_response)
            except ValueError:
                raise APIException("APIResponse received a response which is not valid JSON.")
            else:
                self.res_obj = {"status_code": self.status_code, "data": data_dict}
                self.data = data_dict
                if not self.success:
                    try:
                        self.error_message = self.data["message"]
                    except KeyError:
                        raise APIException("Unexpected error format.")

    def as_dict(self):
        attribute_dict = {
            "res_obj": self.res_obj,
            "success": self.success,
            "data": self.data
        }
        try:
            attribute_dict.update({"status_code": self.status_code})
        except AttributeError:
            pass
        return attribute_dict


    @classmethod
    def from_http_response(cls, http_response, err_message=""):
        assert isinstance(http_response, HTTPResponse)
        return cls(http_response.read(), success=(http_response.status == 200), status_code=http_response.status, err_message=err_message)


    #
    # set_success_status
    # -------------------
    # This method sets the response success status
    def set_success_status(self, status):
        self.success = status
