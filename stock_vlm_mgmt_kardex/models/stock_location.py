# Copyright 2023 Tecnativa - David Vidal
# Copyright 2026 Tecnativa - Adasat Torres
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models

from .kardex_request import KardexRequest


class StockLocation(models.Model):
    _inherit = "stock.location"

    vlm_vendor = fields.Selection(
        selection_add=[
            ("kardex", "Kardex"),
        ],
    )
    format_expression = fields.Char(
        string="Socket Message Format",
        help=(
            "Message template using placeholders such as {task_type},{task_id},{qty}. "
            "Commas are replaced with the configured separator. "
            "Available keys: task_type, task_id, address, carrier, pos_x, pos_y, "
            "qty, info1, info2, info3, info4."
        ),
    )
    separator = fields.Char(
        default=";",
        help="Field separator used in socket requests and responses.",
    )
    format = fields.Char(
        string="Socket Format",
        help=(
            "Ordered response field names, separated by the configured separator. "
            "For example, with a semicolon separator: task_type;task_id;qty."
        ),
    )
    response_code_key = fields.Char(
        default="task_type",
        help="Key in the parsed response that contains the response code.",
    )

    def _kardex_vlm_connector(self) -> KardexRequest:
        """Return the Kardex TCP connector class."""
        return KardexRequest

    def send_vlm_request(self, data, **options):
        """Pass the Kardex message configuration to the VLM connector.

        For Kardex tray calls, skip waiting for a device response so the
        caller can continue immediately after sending the request.

        :param data: Request values passed to the VLM connector.
        :param options: Additional connector options.
        :return: Result of the parent implementation.
        """
        if self.vlm_vendor == "kardex":
            options["format_expression"] = self.format_expression
            options["separator"] = self.separator
            options["format"] = self.format
            options["response_code_key"] = self.response_code_key
            if self.env.context.get("vlm_tray_call"):
                options["ignore_response"] = True
        return super().send_vlm_request(data, **options)
