# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import socket
from unittest.mock import patch

from odoo.tests.common import BaseCase

from ..models import kardex_request


class TestKardexRequest(BaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.keys = (
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
        )
        cls.expression = ",".join("{" + key + "}" for key in cls.keys)
        cls.request_data = {
            "task_type": "put",
            "task_id": "001",
            "address": "21",
            "carrier": "6",
            "pos_x": "7",
            "pos_y": "1",
            "qty": 40,
            "info1": "PICK002",
            "info2": "MAT02",
            "info3": "Condensador",
            "info4": "",
        }

    def setUp(self):
        super().setUp()
        self.data = self.request_data.copy()
        self.client = kardex_request.KardexRequest(
            "127.0.0.1",
            5000,
            format_expression=self.expression,
            separator=";",
            format=";".join(self.keys),
            response_code_key="task_type",
        )
        patcher = patch.object(kardex_request.socket, "socket")
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)
        self.device = self.factory.return_value.__enter__.return_value

    def test_parse_request(self):
        self.assertEqual(
            self.client.parse_request(self.data),
            "3;001;21;6;7;1;40;PICK002;MAT02;Condensador;\r\n",
        )
        self.factory.assert_not_called()

    def test_request_operation_codes(self):
        self.client.format_expression = "{task_type},{task_id}"
        for operation, code in (
            ("release", "0"),
            ("put", "3"),
            ("get", "4"),
            ("count", "5"),
            ("0", "0"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("unknown", "unknown"),
        ):
            with self.subTest(operation=operation):
                data = dict(self.request_data, task_type=operation)
                self.assertEqual(self.client.parse_request(data), f"{code};001\r\n")

    def test_request_separator(self):
        for separator in (",", "|", "\t"):
            with self.subTest(separator=separator):
                self.client.separator = separator
                self.client.format_expression = "{task_id},{qty},{info4}"
                self.assertEqual(
                    self.client.parse_request(self.data),
                    separator.join(("001", "40", "")) + "\r\n",
                )

    def test_request_field_order_and_numeric_format(self):
        self.client.format_expression = "{info2},{task_id},{qty:d}"
        self.assertEqual(self.client.parse_request(self.data), "MAT02;001;40\r\n")

    def test_parse_response(self):
        response = self.client.parse_response(
            "0;001;21;6;7;1;25;PICK002;MAT02;Condensador;"
        )
        self.assertEqual(
            response,
            dict(self.data, task_type="0", qty="25"),
        )

    def test_response_separator_and_order(self):
        self.client.separator = "|"
        self.client.format = "qty|task_id|result"
        self.assertEqual(
            self.client.parse_response("25|001|0"),
            {"qty": "25", "task_id": "001", "result": "0"},
        )

    def test_incomplete_response(self):
        self.client.format = "task_type;task_id;qty"
        self.assertEqual(
            self.client.parse_response("0;001"),
            {"task_type": "0", "task_id": "001", "qty": None},
        )

    def test_extra_response_fields(self):
        self.client.format = "task_type;task_id"
        self.assertEqual(
            self.client.parse_response("0;001;extra"),
            {"task_type": "0", "task_id": "001"},
        )

    def test_send_without_waiting_for_response(self):
        self.client.ignore_response = True
        self.data["info3"] = "Artículo"
        response = self.client.request_operation(self.data)
        self.device.connect.assert_called_once_with(("127.0.0.1", 5000))
        self.device.sendall.assert_called_once_with(
            "3;001;21;6;7;1;40;PICK002;MAT02;Artículo;\r\n".encode()
        )
        self.assertEqual(response, {"code": "0", "task_id": "001"})
        self.device.recv.assert_not_called()

    def test_connection_refused(self):
        self.device.connect.side_effect = ConnectionRefusedError
        self.assertEqual(
            self.client.request_operation(self.data), {"code": "-1", "task_id": "001"}
        )
        self.device.sendall.assert_not_called()

    def test_timeout(self):
        self.client.timeout = 5
        self.device.recv.side_effect = socket.timeout
        self.assertEqual(
            self.client.request_operation(self.data), {"code": "-3", "task_id": "001"}
        )
        self.device.settimeout.assert_called_once_with(5)

    def test_invalid_expression(self):
        self.client.format_expression = "{missing_field}"
        with self.assertRaises(KeyError):
            self.client.request_operation(self.data)
        self.factory.assert_not_called()

    def test_response_without_task_id_field(self):
        self.client.format = "task_type;qty"
        self.device.recv.return_value = b"0;25\r\n"
        self.assertEqual(
            self.client.request_operation(self.data),
            {"task_type": "0", "qty": "25"},
        )
        self.device.recv.assert_called_once_with(1024)

    def test_response_without_task_id_value(self):
        self.client.format = "task_type;task_id;qty"
        for message, task_id, qty in (
            (b"0\r\n", None, None),
            (b"0;;25\r\n", "", "25"),
            (b"0;\r\n", "", None),
        ):
            with self.subTest(message=message):
                self.device.reset_mock()
                self.device.recv.return_value = message
                self.assertEqual(
                    self.client.request_operation(self.data),
                    {"task_type": "0", "task_id": task_id, "qty": qty},
                )
                self.device.recv.assert_called_once_with(1024)

    def test_closed_connection(self):
        self.device.recv.return_value = b""
        self.assertEqual(
            self.client.request_operation(self.data),
            {"code": "-2", "task_id": "001"},
        )
        self.device.recv.assert_called_once_with(1024)

    def test_accept_first_response_with_different_task_id(self):
        self.client.format = "task_type;task_id;qty"
        self.device.recv.side_effect = (b"0;002;10\r\n", b"0;001;25\r\n")
        self.assertEqual(
            self.client.request_operation(self.data),
            {"task_type": "0", "task_id": "002", "qty": "10"},
        )
        self.device.recv.assert_called_once_with(1024)

    def test_request_has_single_crlf_terminator(self):
        for ending in ("", "\n", "\r\n", "\r\n\r\n"):
            with self.subTest(ending=ending):
                self.client.format_expression = "{task_id}" + ending
                self.assertEqual(self.client.parse_request(self.data), "001\r\n")

    def test_intermediate_events(self):
        self.client.format = "task_type;qty"
        self.device.recv.side_effect = (
            b"201;0\r\n",
            b"202;0\r\n",
            b"203;0\r\n",
            b"0;25\r\n",
        )
        self.assertEqual(
            self.client.request_operation(self.data),
            {"task_type": "0", "qty": "25"},
        )
        self.assertEqual(self.device.recv.call_count, 4)

    def test_final_error_codes(self):
        self.client.format = "task_type"
        for code, expected in (("101", "-4"), ("107", "-5"), ("104", "104")):
            with self.subTest(code=code):
                self.device.recv.side_effect = [b"202\r\n", code.encode() + b"\r\n"]
                self.assertEqual(
                    self.client.request_operation(self.data), {"task_type": expected}
                )

    def test_timeout_after_intermediate_event(self):
        self.device.recv.side_effect = [b"201\r\n", socket.timeout]
        self.assertEqual(
            self.client.request_operation(self.data),
            {"code": "-3", "task_id": "001"},
        )

    def test_close_after_intermediate_event(self):
        self.device.recv.side_effect = [b"202\r\n", b""]
        self.assertEqual(
            self.client.request_operation(self.data),
            {"code": "-2", "task_id": "001"},
        )
