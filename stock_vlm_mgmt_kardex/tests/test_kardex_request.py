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
        cls.expression = (
            "(f\"{data['task_type']};{data['task_id']};{data['address']};\""
            "f\"{data['carrier']};{data['pos_x']};{data['pos_y']};{data['qty']};\""
            "f\"{data['info1']};{data['info2']};{data['info3']};{data['info4']}\\r\\n\")"
        )
        cls.request_data = {
            "task_type": "put",
            "task_id": "001",
            "address": "21",
            "carrier": "6",
            "pos_x": "7",
            "pos_y": "1",
            "qty": 40.9,
            "info1": "PICK002",
            "info2": "MAT02",
            "info3": "Condensador",
            "info4": "",
        }

    def setUp(self):
        super().setUp()
        self.data = self.request_data.copy()
        self.client = kardex_request.KardexRequest(
            "127.0.0.1", 5000, format_expression=self.expression
        )
        patcher = patch.object(kardex_request.socket, "socket")
        self.factory = patcher.start()
        self.addCleanup(patcher.stop)
        self.device = self.factory.return_value.__enter__.return_value

    def test_prepare_expression(self):
        self.assertEqual(
            self.client.prepare_data(self.data),
            "put;001;21;6;7;1;40;PICK002;MAT02;Condensador;\r\n",
        )
        self.factory.assert_not_called()

    def test_expression_transformation(self):
        self.client.format_expression = (
            "f\"{data['task_id']}:{data['info2']}:{data['qty']}\""
        )
        self.assertEqual(self.client.prepare_data(self.data), "001:MAT02:40")

    def test_send_and_read_response(self):
        self.device.recv.return_value = (
            b"0;001;21;6;7;1;25;PICK002;MAT02;Condensador;\r\n"
        )
        response = self.client.request_operation(self.data)
        self.device.connect.assert_called_once_with(("127.0.0.1", 5000))
        self.device.sendall.assert_called_once_with(
            b"3;001;21;6;7;1;40;PICK002;MAT02;Condensador;\r\n"
        )
        self.assertEqual(response["code"], "0")
        self.assertEqual(response["task_id"], "001")
        self.assertEqual(response["qty"], "25")

    def test_operation_codes(self):
        self.client.ignore_response = True
        for operation, code in (
            ("put", "3"),
            ("get", "4"),
            ("count", "5"),
            ("release", "0"),
        ):
            with self.subTest(operation=operation):
                self.device.reset_mock()
                response = self.client.request_operation(
                    dict(self.request_data, task_type=operation)
                )
                message = self.device.sendall.call_args.args[0]
                self.assertEqual(message.split(b";")[0], code.encode())
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
        self.client.format_expression = "data['missing_field']"
        with self.assertRaises(ValueError):
            self.client.request_operation(self.data)
        self.factory.assert_not_called()
