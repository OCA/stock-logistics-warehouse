# Copyright 2023 Tecnativa - David Vidal
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

    def _kardex_vlm_connector(self) -> KardexRequest:
        """Wildcarded method to return our vendor specific connector"""
        return KardexRequest

    def send_vlm_request(self, data, **options):
        """The tray call in Kardex doesn't return anything, so we can release the
        thread immediately"""
        if self.vlm_vendor == "kardex" and self.env.context.get("vlm_tray_call"):
            options["ignore_response"] = True
        return super().send_vlm_request(data, **options)
