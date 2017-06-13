#
# cp_management_api.py
# version 1.1
#
# A library for communicating with Check Point's management server using [2.7.9 < python < 3]
# written by: Check Point software technologies inc.
# October 2016
# tested with Check Point R80 (tested with take hero2 198)
#

from __future__ import print_function

import hashlib
import httplib
import json
import os.path
import ssl
import subprocess
import sys
import time
from distutils.version import LooseVersion

from api_exceptions import APIException, APIClientException
from api_response import APIResponse


#
#
# APIClient encapsulates everything that the user needs to do for communicating with a Check Point management server
#
#

# This class provides arguments for APIClient configuration.
# All the arguments are configured with their default values.
class APIClientArgs:
    # port is set to None by default, but it gets replaced with 443 if not specified
    def __init__(self, port=None, fingerprint=None, sid=None, server=None, domain=None, http_debug_level=0,
                 api_calls=None, debug_file="", proxy_host=None, proxy_port=8080, proxy_protocol="http",
                 api_version="1.0"):
        self.port = port
        self.fingerprint = fingerprint  # management server fingerprint
        self.sid = sid  # session-id.
        self.server = server  # management server name or IP-address
        self.domain = domain  # domain to log into in an MDS environment
        self.http_debug_level = http_debug_level  # debug level
        self.api_calls = api_calls if api_calls else []  # an array with all the api calls (for debug purposes)
        self.debug_file = debug_file  # name of debug file. If left empty, debug data will not be saved to disk.
        self.proxy_host = proxy_host  # HTTP proxy server address
        self.proxy_port = proxy_port  # HTTP proxy port
        self.proxy_protocol = proxy_protocol  # currently only http and https are supported
        self.api_version = api_version  # Management server's API version


class APIClient:
    #
    # initialize class
    #
    def __init__(self, api_client_args=None):
        # if a client_args is not supplied, make a default one
        if api_client_args is None:
            api_client_args = APIClientArgs()
        self.__port, self.__is_port_default = (api_client_args.port, False) if api_client_args.port else (443, True)  # port on management server
        self.fingerprint = api_client_args.fingerprint  # management server fingerprint
        self.sid = api_client_args.sid  # session-id.
        self.server = api_client_args.server  # management server name or IP-address
        self.domain = api_client_args.domain  # domain to log into in an MDS environment
        self.http_debug_level = api_client_args.http_debug_level  # debug level
        self.api_calls = api_client_args.api_calls  # an array with all the api calls (for debug purposes)
        self.debug_file = api_client_args.debug_file  # name of debug file. If left empty, debug data will not be saved to disk.
        self.proxy_host = api_client_args.proxy_host  # HTTP proxy server address
        self.proxy_port = api_client_args.proxy_port  # HTTP proxy port
        self.proxy_protocol = api_client_args.proxy_protocol  # currently only http and https are supported
        self.api_version = api_client_args.api_version  # Management server's API version

    def __enter__(self):
        return self

    #
    # destructor
    #
    def __exit__(self, exc_type, exc_value, traceback):

        # if sid is not empty (the login api was called), then call logout
        if self.sid:
            self.api_call("logout")
        # save debug data with api calls to disk
        self.save_debug_data()


    def get_port(self):
        return self.__port

    # return whether the user changed the port
    def is_port_default(self):
        return self.__is_port_default

    def set_port(self, port):
        self.__port = port
        self.__is_port_default = False

    #
    # save_debug_data
    # ----------------------------------------------------
    # save debug data with api calls to disk
    #
    def save_debug_data(self):
        if self.debug_file != "":
            print("\nSaving data to debug file {}\n".format(self.debug_file), file=sys.stderr)
            out_file = open(self.debug_file, 'w+')
            out_file.write(json.dumps(self.api_calls, indent=4, sort_keys=True))

    #
    # login
    # ----------------------------------------------------
    # performs a 'login' API call to the management server
    #
    # arguments:
    #    server    - the IP address or name of the Check Point management server
    #    user      - Check Point admin name
    #    password  - Check Point admin password
    #    continue-last-session - [optional] it is possible to continue the last Check Point session or to create a new one
    #    domain    - [optional] the name, UID or IP-Address of the domain to login.
    #    payload   - More settings for the login command
    #
    # return: APIResponse object
    # side-effects: updates the class's uid and server variables
    #
    #
    def login(self, server, user, password, continue_last_session=False, domain=None, read_only=False, payload=None):
        credentials = {"user": user, "password": password, "continue-last-session": continue_last_session, "read-only": read_only}

        if domain:
            credentials.update({"domain": domain})
        if isinstance(payload, dict):
            credentials.update(payload)
        login_res = self.api_call("login", credentials, server)

        if login_res.success:
            self.sid = login_res.data["sid"]
            self.server = server
            self.domain = domain
            self.api_version = login_res.data["api-server-version"]
        return login_res

    #
    # login_as_root
    # ---------------------------------------------
    # This method allows to login into the management server with root permissions.
    # In order to use this method the application should be run directly on the management server
    # and to have super-user privileges.
    #
    # arguments:
    #     domain  - [optional] name/uid/IP address of the domain you want to log into in an MDS environment
    #     payload - [optional] dict of additional parameters for the login command
    # return:
    #     APIResponse object with the relevant details from the login command.
    def login_as_root(self, domain=None, payload=None):
        python_absolute_path = os.path.expandvars("$MDS_FWDIR/Python/bin/python")
        api_get_port_absolute_path = os.path.expandvars("$MDS_FWDIR/scripts/api_get_port.py")
        mgmt_cli_absolute_path = os.path.expandvars("$CPDIR/bin/mgmt_cli")
        # try to get the management server's port by running a script
        if not self.is_port_default():
            port = self.get_port()
        else:
            try:
                port = json.loads(subprocess.check_output([python_absolute_path, api_get_port_absolute_path, "-f", "json"]))["external_port"]
            # if can't, default back to what the user wrote or the default (443)
            except (ValueError, subprocess.CalledProcessError):
                port = self.get_port()
        try:
            # This simple dict->cli format works only because the login command doesn't require
            # any complex parameters like objects and lists
            new_payload = []
            if payload:
                for key in payload.keys():
                    new_payload += [key, payload[key]]
            if domain:
                new_payload += ["domain", domain]
            login_response = json.loads(subprocess.check_output([mgmt_cli_absolute_path, "login", "-r", "true", "-f", "json", "--port", str(port)] + new_payload))
            self.sid = login_response["sid"]
            self.server = "127.0.0.1"
            self.domain = domain
            self.api_version = login_response["api-server-version"]
            return APIResponse(login_response, success=True)
        except ValueError as err:
            raise APIClientException(
                "Could not load JSON from login as root command, perhaps no root privileges?\n" + str(
                    type(err)) + " - " + str(err))
        except subprocess.CalledProcessError as err:
            raise APIClientException("Could not login as root:\n" + str(type(err)) + " - " + str(err))

    #
    # gen_api_query
    # ----------------------------------------------------
    # This is a generator function that yields the list of wanted objects received so far from the management server.
    # This is in contrast to normal API calls that return only a limited number of objects.
    # This function can be used to show progress when requesting many objects (i.e. "Received x/y objects.")
    #
    # arguments:
    #    command        - name of API command. This command should be an API that returns an array of objects (for example: show-hosts, show networks, ...)
    #    details-level  - query APIs always take a details-level argument. possible values are "standard", "full", "uid"
    #    container_key  - the field in the .data dict that contains the objects
    # return: an APIResponse object as detailed above
    #
    def gen_api_query(self, command, details_level="standard", container_keys=None, payload=None):
        limit = 50  # each time get no more than 50 objects
        finished = False  # will become true after getting all the data
        all_objects = {}  # accumulate all the objects from all the API calls

        # default
        if container_keys is None:
            container_keys = ["objects"]
        # if given a string, make it a list
        if isinstance(container_keys, basestring):
            container_keys = [container_keys]
        for key in container_keys:
            all_objects[key] = []
        iterations = 0  # number of times we've made an API call
        if payload is None:
            payload = {}

        payload.update({"limit": limit, "offset": iterations * limit, "details-level": details_level})
        api_res = self.api_call(command, payload)
        for container_key in container_keys:
            if container_key not in api_res.data or not isinstance(api_res.data[container_key], list) \
                    or "total" not in api_res.data or api_res.data["total"] == 0:
                finished = True
                yield api_res
                break
        # are we done?
        while not finished:
            # make the API call, offset should be increased by 'limit' with each iteration

            if api_res.success is False:
                raise APIException(api_res.error_message)

            total_objects = api_res.data["total"]  # total number of objects
            received_objects = api_res.data["to"]  # number of objects we got so far
            for container_key in container_keys:
                all_objects[container_key] += api_res.data[container_key]
                api_res.data[container_key] = all_objects[container_key]
            # yield the current result
            yield api_res
            # did we get all the objects that we're supposed to get
            if received_objects == total_objects:
                break

            iterations += 1
            payload.update({"limit": limit, "offset": iterations * limit, "details-level": details_level})
            api_res = self.api_call(command, payload)

    #
    # api_call
    # ----------------------------------------------------
    # performs a web-service API request to the management server
    #
    # arguments:
    #    command       - the command is placed in the URL field
    #    payload       - a JSON object (or a string representing a JSON object) with the command arguments
    #    server        - [optional]. The Check Point management server. when omitted use self.server.
    #    sid           - [optional]. The Check Point session-id. when omitted use self.sid.
    #    wait_for_task - dertermines the behavior when the API server responds with a "task-id".
    #                    by default, the function will periodically check the status of the task
    #                    and will not return until the task is completed.
    #                    when wait_for_task=False, it is up to the user to call the "show-task" API and check
    #                    the status of the command.
    #
    # return: APIResponse object
    # side-effects: updates the class's uid and server variables
    #
    #
    def api_call(self, command, payload=None, server=None, sid=None, wait_for_task=True):
        if payload is None:
            payload = {}
        # convert the json payload to a string if needed
        if isinstance(payload, str):
            _data = payload
        elif isinstance(payload, dict):
            _data = json.dumps(payload, sort_keys=False)
        else:
            raise TypeError('Invalid payload type - must be dict/string')
        # update class members if needed.
        if server is None:
            server = self.server
        if sid is None:
            sid = self.sid

        # set headers
        _headers = {
            "User-Agent": "python-api-wrapper",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Content-Length": len(_data)
        }

        # in all API calls (except for 'login') a header containing the Check Point session-id is required.
        if sid is not None:
            _headers["X-chkp-sid"] = sid

        # create ssl context with no ssl verification, we do it by ourselves
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # create https connection
        conn = HTTPSConnection(server, self.get_port(), context=context)

        # set fingerprint
        conn.fingerprint = self.fingerprint

        # set debug level
        conn.set_debuglevel(self.http_debug_level)
        url = "/web_api/" + command

        try:
            # send the data to the Check Point server
            conn.request("POST", url, _data, _headers)
            # get the response from the Check Point server
            response = conn.getresponse()
            res = APIResponse.from_http_response(response)

        except ValueError as err:
            if err.args[0] == "fingerprint value mismatch":
                err_message = "Error: Fingerprint value mismatch:\n" + " Expecting : {}\n".format(err.args[1]) + " Got: {}\n".format(err.args[2]) + "if you trust the new fingerprint, edit the 'fingerprints.txt' file."
                res = APIResponse("", False, err_message=err_message)
            else:
                res = APIResponse("", False, err_message=err)
        except Exception as inst:
            res = APIResponse("", False, err_message=inst)

        # when the command is 'login' we'd like to convert the password to "****" so that it would not appear in the debug file.
        if command == "login":
            json_data = json.loads(_data)
            json_data["password"] = "****"
            _data = json.dumps(json_data)

        # store the request and the response (for debug purpose).
        _api_log = {
            "request": {
                "url": url,
                "payload": json.loads(_data),
                "headers": _headers
            },
            "response": res.res_obj
        }
        self.api_calls.append(_api_log)

        # If we want to wait for the task to end, wait for it
        if wait_for_task is True and res.success and command != "show-task":
            if "task-id" in res.data:
                res = self.__wait_for_task(res.data["task-id"])
            elif "tasks" in res.data:
                res = self.__wait_for_tasks(res.data["tasks"])

        return res

    #
    # get_server_fingerprint
    # ----------------------------------------------------
    # initiates an HTTPS connection to the server and extracts the SHA1 fingerprint from the server's certificate.
    #
    # arguments:
    #    server    - the IP address or name of the Check Point managemenet server
    #
    # return: string with SHA1 fingerprint (all uppercase letters)
    #
    def get_server_fingerprint(self, server):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        conn = HTTPSConnection(server, self.get_port(), context=context)
        return conn.get_fingerprint_hash()

    #
    # __wait_for_task
    # ----------------------------------------------------
    # When the server needs to perform an API call that may take a long time (e.g. run-script, install-policy, publish),
    # the server responds with a 'task-id'.
    # Using the show-task API it is possible to check on the status of this task until its completion.
    # Every two seconds, this function will check for the status of the task.
    # The function will return when the task (and its subtasks) are no longer in-progress.
    #
    # arguments:
    #    task-id       - the task identifier
    #
    def __wait_for_task(self, task_id):
        task_complete = False
        task_result = None
        in_progress = "in progress"

        # as long as there is a task in progress
        while not task_complete:

            # check the status of the task
            task_result = self.api_call("show-task", {"task-id": task_id, "details-level": "full"}, self.server,
                                        self.sid, False)

            if task_result.success is False:
                raise Exception("ERROR: failed to handle asynchronous tasks as synchronous, tasks result is undefined")
            # count the number of tasks that are not in-progress
            completed_tasks = sum(1 for task in task_result.data["tasks"] if task["status"] != in_progress)

            # get the total number of tasks
            total_tasks = len(task_result.data["tasks"])

            # are we done?
            if completed_tasks == total_tasks:
                task_complete = True
            else:
                time.sleep(2)  # wait 2 sec

        self.check_tasks_status(task_result)
        return task_result

    #
    # __wait_for_tasks
    # ----------------------------------------------------
    # The version of __wait_for_task function for the collection of tasks

    # arguments:
    #    tasks      - A list of tasks identifiers
    #
    def __wait_for_tasks(self, task_objects):

        # A list of task ids to be retrieved
        tasks = []
        for taskObject in task_objects:
            # Retrieve the taskId and wait for the task to be completed
            taskId = taskObject["task-id"]
            tasks.append(taskId)
            self.__wait_for_task(taskId)

        task_result = self.api_call("show-task", {"task-id": tasks, "details-level": "full"}, self.server,
                                    self.sid, False)

        APIClient.check_tasks_status(task_result)
        return task_result


    #
    # check_tasks_status
    # --------------------
    # This method checks if one of the tasks failed and if so, changes the response status to be False
    #
    # arguments:
    #   task_result - api_response returned from "show-task" command
    #
    #
    @staticmethod
    def check_tasks_status(task_result):
        for task in task_result.data["tasks"]:
            if task["status"] == "failed" or task["status"] == "partially succeeded":
                task_result.set_success_status(False)
                break

    #
    # api_query
    # ----------------------------------------------------
    # The APIs that return a list of objects are limited by the number of objects that they return.
    # To get the full list of objects, there's a need to make repeated API calls each time using a different offset
    # until all the objects are returned.
    # This API makes such repeated API calls and return the full list objects.
    # note: this function calls gen_api_query and iterates over the generator until it gets all the objects, then returns.
    #
    # arguments:
    #    command        - name of API command. This command should be an API that returns an array of objects (for example: show-hosts, show networks, ...)
    #    details-level  - query APIs always take a details-level argument. possible values are "standard", "full", "uid"
    #    container-key  - name of the key that holds the objects in the JSON response (usually "obejcts")
    #    include-container-key - If set to False the 'data' field of the APIResponse object will be a list of the wanted objects.
    #                            Otherwiae, the date field of the APIResponse will be a dictionary in the following foemat: { container_key: [ List of the wanted objects], "total": size of the list}
    #
    # return:
    #     if include-container-key is False: an APIResponse object whose .data member contains a list of the objects requested: [ , , , ...]
    #     if include-container-key is True:  an APIResponse object whose .data member contains a dict: { container_key: [...], "total": n }
    #
    def api_query(self, command, details_level="standard", container_key="objects", include_container_key=False):
        for api_res in self.gen_api_query(command, details_level, [container_key]):
            if api_res.data["total"] == len(api_res.data[container_key]):
                if "from" in api_res.data:
                    del api_res.data["from"]
                if "to" in api_res.data:
                    del api_res.data["to"]
        if include_container_key is False:
            api_res.data = api_res.data[container_key]
        return api_res

    #
    # check_fingerprint
    # ----------------------------------------------------
    # This function checks if the server's certificate is stored in the local fingerprints file.
    # If the server fingerprint is not found, it makes an https connection to the server and asks the user if he accepts the server fingerprint.
    # If the fingerprint is trusted, then it is stored in the fingerprint file.
    #
    #
    # arguments:
    #    server         - IP address / name of the Check Point management server
    #
    # return: false if the user does not accept the server certificate, 'true' in all other cases.
    #
    def check_fingerprint(self, server):
        # read the fingerprint from the local file
        local_fingerprint = self.read_fingerprint_from_file(server)
        server_fingerprint = self.get_server_fingerprint(server)

        # if the fingerprint is not stored on the local file
        if local_fingerprint == "" or local_fingerprint.replace(':', '').upper() != server_fingerprint.replace(':',
                                                                                                               '').upper():
            # Get the server's fingerprint with a socket.
            if server_fingerprint == "":
                return False
            if local_fingerprint == "":
                print("You currently do not have a record of this server's fingerprint.", file=sys.stderr)
            else:
                print(
                    "The server's fingerprint is different from your local record of this server's fingerprint.\nYou maybe a victim to a Man-in-the-middle attack, please beware.",
                    file=sys.stderr)
            print("Server's fingerprint: {}".format(server_fingerprint), file=sys.stderr)
            if self.ask_yes_no_question("Do you accept this fingerprint?"):
                if self.save_fingerprint_to_file(server, server_fingerprint):  # Save it.
                    print("Fingerprint saved.", file=sys.stderr)
                else:
                    print("Could not save fingerprint to file. Continuing anyway.", file=sys.stderr)
            else:
                return False
        self.fingerprint = server_fingerprint  # set the actual fingerprint in the class instance
        return True

    #
    # ask_yes_no_question
    # ----------------------------------------------------
    # helper function. Present a question to the user with Y/N options.
    #
    # arguments:
    #    question         - the question to display to the user
    #
    # return: 'True' if the user typed 'Y'. 'False' is the user typed 'N'
    #
    @staticmethod
    def ask_yes_no_question(question):
        answer = raw_input(question + " [y/n] ")
        if answer.lower() == "y" or answer.lower() == "yes":
            return True
        else:
            return False

    #
    # compare_versions
    # ----------------------------------------------------
    # helper function. Compares two strings of version numbers -> "1.2.1" > "1.1", "0.9.0" == "0.9"
    # using distutils.version
    #
    # arguments:
    #    version1
    #    version2
    # return:
    #  1 -> version1 >  version2
    #  0 -> version1 == version2
    # -1 -> version1 <  version2
    @staticmethod
    def compare_versions(version1, version2):
        return int(LooseVersion(version1) >= LooseVersion(version2)) - int(LooseVersion(version1) <= LooseVersion(version2))

    #
    # save_fingerprint_to_file
    # ----------------------------------------------------
    # store a server's fingerprint into a local file.
    #
    # arguments:
    #    server         - the IP address/name of the Check Point management server.
    #    fingerprint    - A SHA1 fingerprint of the server's certificate.
    #    filename       - The file in which to store the certificates. The file will hold a JSON structure in which the key is the server and the value is its fingerprint.
    #
    # return: 'True' if everything went well. 'False' if there was some kind of error storing the fingerprint.
    #
    @staticmethod
    def save_fingerprint_to_file(server, fingerprint, filename="fingerprints.txt"):
        if not fingerprint:
            return False
        if os.path.isfile(filename):
            try:
                with open(filename) as file:
                    json_dict = json.load(file)
            except ValueError as e:
                if e.message == "No JSON object could be decoded":
                    print("Corrupt JSON file: " + filename, file=sys.stderr)
                else:
                    print(e.message, file=sys.stderr)
                return False
            except IOError as e:
                print("Couldn't open file: " + filename + "\n" + e.message, file=sys.stderr)
                return False
            except Exception as e:
                print(e, file=sys.stderr)
                return False
            else:
                if server in json_dict and json_dict[server] == fingerprint:
                    return True
                else:
                    json_dict[server] = fingerprint
        else:
            json_dict = {server: fingerprint}
        try:
            with open(filename, 'w') as filedump:
                json.dump(json_dict, filedump, indent=4, sort_keys=True)
                filedump.close()
            return True
        except IOError as e:
            print("Couldn't open file: " + filename + " for writing.\n" + e.message, file=sys.stderr)
        except Exception as e:
            print(e, file=sys.stderr)
            return False

    #
    # read_fingerprint_from_file
    # ----------------------------------------------------
    # reads a server's fingerprint from a local file.
    #
    # arguments:
    #    server         - the IP address/name of the Check Point management server.
    #    filename       - The file in which to store the certificates. The file will hold a JSON structure in which the key is the server and the value is its fingerprint.
    #
    # return: A SHA1 fingerprint of the server's certificate.
    #
    @staticmethod
    def read_fingerprint_from_file(server, filename="fingerprints.txt"):
        assert isinstance(server, basestring)

        if os.path.isfile(filename):
            try:
                with open(filename) as file:
                    json_dict = json.load(file)
            except ValueError as e:
                if e.message == "No JSON object could be decoded":
                    print("Corrupt JSON file: " + filename, file=sys.stderr)
                else:
                    print(e.message, file=sys.stderr)
            except IOError as e:
                print("Couldn't open file: " + filename + "\n" + e.message, file=sys.stderr)
            except Exception as e:
                print(e, file=sys.stderr)
            else:
                # file is ok and readable.
                if server in json_dict:
                    return json_dict[server]
        return ""


#
#
# HTTPSConnection
# ----------------------------------------------------
# A class for making HTTPS connections that overrides the default HTTPS checks (e.g. not accepting self-signed-certificates) and replaces them with a server fingerprint check
#
#
class HTTPSConnection(httplib.HTTPSConnection):
    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock = ssl.wrap_socket(
            self.sock, self.key_file, self.cert_file,
            cert_reqs=ssl.CERT_NONE)
        if getattr(self, 'fingerprint') is not None:
            digest = self.fingerprint
            alg = "SHA1"
            fingerprint = hashlib.new(alg, self.sock.getpeercert(True)).hexdigest().upper()
            if fingerprint != digest.replace(':', '').upper():
                raise ValueError('fingerprint value mismatch', fingerprint, digest.replace(':', '').upper())

    def get_fingerprint_hash(self):
        try:
            httplib.HTTPConnection.connect(self)
            self.sock = ssl.wrap_socket(self.sock, self.key_file, self.cert_file, cert_reqs=ssl.CERT_NONE)
        except Exception as err:
            return ""
        fingerprint = hashlib.new("SHA1", self.sock.getpeercert(True)).hexdigest()
        return fingerprint.upper()

