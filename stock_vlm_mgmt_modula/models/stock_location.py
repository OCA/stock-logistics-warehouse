# Copyright 2024 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models

from .modula_request import ModulaRequest


class StockLocation(models.Model):
    _inherit = "stock.location"

    vlm_vendor = fields.Selection(
        selection_add=[
            ("modula", "Modula"),
        ],
    )

    def _modula_vlm_connector(self):
        return ModulaRequest
