# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    def _check_storage_type(self):
        # disable the checks when placing goods in vertical lift cells:
        # we still want to benefit of the storage type rules to select
        # a destination, but we want to allow selecting a different tray
        # type
        self = self.filtered(
            lambda quant: quant.location_id.vertical_lift_kind != "cell"
        )
        super()._check_storage_type()
