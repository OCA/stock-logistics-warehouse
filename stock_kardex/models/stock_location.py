# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    kardey_tray = fields.Boolean()
    kardex_tray_type_id = fields.Many2one(
        comodel_name="stock.kardex.tray.type",
        ondelete="restrict",
        # TODO: later, we'll want a wizard to change the type,
        # that will check if the sublocations are empty before
        # changing. It will disable the sublocations and create
        # new ones according to the tray disposition. This field
        # will then be readonly.
        # readonly=True,
    )
