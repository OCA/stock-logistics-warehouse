# Copyright 2022 Tecnativa - David Vidal
# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
import socket

_logger = logging.getLogger(__name__)


KARDEX_OPERATION_CODES = {
    "release": "0",
    "put": "3",
    "get": "4",
    "count": "5",
}


KARDEX_INTERMEDIATE_CODES = frozenset({"201", "202", "203"})
KARDEX_RESPONSE_CODES = {"101": "-4", "107": "-5"}


class KardexRequest:
    """TCP client for Kardex SVM task requests and responses.

    Requests use a configurable ``format_expression`` template with named
    placeholders from the input dictionary. After interpolation, all commas
    are replaced with ``separator``. Each request ends with a single CRLF
    terminator, appended automatically after removing trailing CR/LF characters.

    Responses use the ordered field names in ``format``, split by the same
    separator. The field named by ``response_code_key`` is used to interpret
    device codes. Responses do not require a task identifier.

    A typical semicolon-separated message contains task_type, task_id,
    address, carrier, pos_x, pos_y, qty, and info1 through info4. The device
    may return an adjusted quantity after the operator completes the task.
    """

    def __init__(self, ip, port, timeout=0, **options):
        """Configure the device connection and message serialization.

        :param ip: Device IP address or hostname.
        :param port: TCP port, converted to an integer.
        :param timeout: Receive timeout in seconds; zero leaves reads blocking.
        :param options: Message template (format_expression), response field
            order (format), field separator (separator), response code field
            (response_code_key), and whether to skip reads (ignore_response).
        """
        self.ip = ip
        self.port = int(port)
        self.timeout = timeout
        self.ignore_response = options.get("ignore_response")
        self.format_expression = options.get("format_expression")
        self.format = options.get("format")
        self.separator = options.get("separator")
        self.response_code_key = options.get("response_code_key")

    def parse_response(self, response):
        """Map separated response values to the configured field names.

        Values remain strings, including any whitespace or line terminators.
        Missing values are set to None and extra values are ignored.

        :param response: Decoded device response.
        :return: Dictionary keyed by the field names in ``format``.
        """
        keys = self.format.split(self.separator)
        parsed_response = dict.fromkeys(keys, None)
        parsed_response.update(zip(keys, response.split(self.separator), strict=False))
        return parsed_response

    def parse_request(self, data):
        """Interpolate the request template and replace commas with the separator.

        Replacement also affects commas inside interpolated values. Trailing
        CR/LF characters are replaced with a single CRLF terminator.

        :param data: Dictionary containing the template placeholder values.
        :return: Formatted message ready for UTF-8 encoding.
        :raises KeyError: If a template placeholder is missing from data.
        """
        data.update(
            {
                "task_type": KARDEX_OPERATION_CODES.get(
                    data.get("task_type"), data.get("task_type")
                ),
                "qty": int(float(data["qty"])),
            }
        )
        message = self.format_expression.format_map(data)
        return message.replace(",", self.separator).rstrip("\r\n") + "\r\n"

    def request_operation(self, data):
        """Send a task over TCP and optionally wait for a final CRLF-delimited response.

        Each socket read is expected to contain one complete response.
        Events 201, 202 and 203 are intermediate; wait for confirmation after
        carrier arrival. Task identifiers are not checked. Device codes 101 and 107
        are mapped to -4 and -5 in the configured response code field.
        Connection refusal, a closed connection, and receive timeout
        return codes -1, -2, and -3 respectively under the ``code`` key.
        When reads are skipped, return code 0 and the submitted task ID.

        :param data: Template values, including task_id for status dictionaries.
        :return: Parsed final response or a code/task_id status dictionary.
        """
        message = self.parse_request(data)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as device:
            try:
                device.connect((self.ip, self.port))
            except ConnectionRefusedError:
                return {"code": "-1", "task_id": data["task_id"]}
            device.sendall(message.encode("utf-8"))
            # Open the request with the optional timeout so the thread isn't halted
            # forever
            if self.timeout:
                device.settimeout(self.timeout)
            if self.ignore_response:
                return {"code": "0", "task_id": data["task_id"]}
            while True:
                try:
                    message = device.recv(1024).decode("utf-8")
                except socket.timeout:
                    return {"code": "-3", "task_id": data["task_id"]}
                if not message:
                    return {"code": "-2", "task_id": data["task_id"]}
                message = message.rstrip("\r\n")
                _logger.info("Kardex response: %s", message)
                response = self.parse_response(message)
                code = response.get(self.response_code_key) or "-999"
                if code in KARDEX_INTERMEDIATE_CODES:
                    continue
                response[self.response_code_key] = KARDEX_RESPONSE_CODES.get(code, code)
                return response
