# Copyright 2022 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import socket

_logger = logging.getLogger(__name__)

KARDEX_KEYS = [
    "task_type",
    "task_id",
    "address",
    "carrier",
    "pos_x",
    "pos_y",
    "qty",
    "info1",
    "info2",
    "info3",
    "info4",
]


KARDEX_OPERATION_CODES = {
    "release": "0",
    "put": "3",
    "get": "4",
    "count": "5",
}


class KardexRequest:
    """
    Interface to Kardex SVMs

    To command tasks we send a tcp message to the SVM with this format

    TASK_TYPE;TASK_ID;ADDRESS;CARRIER;POS_X;POS_Y;QTY;INFO1;INFO2;INFO3;INFO4<CR><LF>

    Each task is enqueued in the SVM and every time it gets finished it returns a
    response with a success or error code (0 or 101).

    - TASK_TYPE is configured at the machine itself.
    - TASK_ID would be a unique id we give to the task so we can identify it when
      the JMIF server responds back.
    - ADDRESS: Which device to call.
    - CARRIER: The tray we want to call
    - POSX, POSY: Show the user where the items are located inside the tray
    - QTY: How many items to get from the SVM
    - The INFO fields are optional to show the user usefull info for the pick.

    An example call:
    3;001;21;6;7;1;40;PICK002;MAT02;Capacitor 40 mV;Check they're ok<CR><LF>

    The message will get to the SVM screen. When the user finishes, the SVM will respond
    back with a success message. Notice that in this response, the quantity has been
    changed by the user:
    0;001;21;6;7;1;25;PICK002;MAT02;Capacitor 40 mV;Check they're ok<CR><LF>

    If there'd be an error in the process we'd get an error:
    101;001;21;6;7;1;40;PICK002;MAT02;Capacitor 40 mV;Check they're ok<CR><LF>

    If we want to release the carriers, we can call the carrier 0
    0;465;21;0;0;0;0;;;;<CR><LF>
    """

    def __init__(self, ip, port, timeout=0, **options):
        self.ip = ip
        self.port = int(port)
        self.timeout = timeout
        self.ignore_response = options.get("ignore_response")

    def parse_data(self, data):
        """Transforms csv single string into a dictionary that we can work with.
        @param {string} data: semicolon separated values for the kardex payload format
        @return {dict} those csv values transformed into key value pairs
        """
        parsed_data = dict.fromkeys(KARDEX_KEYS, None)
        try:
            parsed_data.update({k: v for k, v in zip(KARDEX_KEYS, data.split(";"))})
        except Exception:
            _logger.debug(f"Exception parsing data: {data}")
        if parsed_data.get("qty"):
            # Strip dots
            parsed_data["qty"] = parsed_data["qty"].replace(".", "")
        return parsed_data

    def prepare_data(self, data):
        """Transforms data dict into kardex csv data string
        @param {dict} data
        @return {string}
        """
        # No support for floats :S
        data["qty"] = int(float(data["qty"]))
        values = [str(v) for v in data.values()]
        return f"{';'.join(values)}\r\n"

    def request_operation(self, data):
        """
        @param {string|dict} we can handle either a dictionary with the KARDEX_KEYS
        format or the csv formatted values in a string (it must end in \r\n)
        @return {dict} with the reponse of the device on the matching task
        """
        if isinstance(data, dict):
            # We receive the task type with a common code. Transform into the Kardex one
            data["task_type"] = KARDEX_OPERATION_CODES.get(data["task_type"], "0")
            data = self.prepare_data(data)
        _logger.info(f"Request: {data}")
        operation_id = self.parse_data(data).get("task_id")
        if not operation_id:
            return
        data = data.encode("utf-8")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as device:
            try:
                device.connect((self.ip, self.port))
            except ConnectionRefusedError:
                return {"code": "-1", "task_id": operation_id}
            device.sendall(data)
            # Open the request with the optional timeout so the thread isn't halted
            # forever
            if self.timeout:
                device.settimeout(self.timeout)
            # Default response
            response = {"code": "0", "task_id": operation_id}
            # TODO: This is uncomplete: when we do the request, we won't receive the
            # response until the VLM user validates the operation from the device screen
            # That's an unknown amount of time.
            # And what if the system is reset in the meantime? We'd loose the original
            # thread and the response would be missed.
            # I guess that's why the c2c module has that proxy thing, so they can be
            # more resilient on that regard or at least to not block the thread waiting
            # for a response.
            while True and not self.ignore_response:
                # TBE: Will this response window be enough to get it in one shot?
                try:
                    res = device.recv(1024).decode("utf-8")
                    _logger.info(res)
                except socket.timeout:
                    response["code"] = "-3"
                    return response
                response = self.parse_data(res)
                # Deal with response codes. Default to unkown issue code
                response["code"] = response.get("task_type", "-999")
                # Code 101 for an issue that happens in the VLM hardware itself
                if response["code"] == "101":
                    response["code"] = "-4"
                # Task cancelled
                if response["code"] == "107":
                    response["code"] = "-5"
                # If it's not our operation we should keep trying
                # TBE: But until when? This locks the current thread so the screen
                # is indeed locked and the user can't do virtually anything about it
                if response["task_id"] == operation_id:
                    break
                if response["task_id"] is None:
                    # Empty response. Unknow reason error. Could be due to a shutdown
                    # of the JMIF service.
                    return {"code": "-2", "task_id": operation_id}
        _logger.info(f"Response: {response}")
        return response
