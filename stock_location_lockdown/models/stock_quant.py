# -*- coding: utf-8 -*-
# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_move(
            self, quants, move, location_to, location_from=False, lot_id=False,
            owner_id=False, src_package_id=False, dest_package_id=False,
            entire_pack=False):
        if (
                location_to.usage == 'internal' and
                location_to.block_stock_entrance):
            raise UserError(_(
                "The location '%s' is not configured to receive stock.")
                % location_to.display_name)
        return super(StockQuant, self).quants_move(
            quants, move, location_to, location_from=location_from,
            lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
            dest_package_id=dest_package_id, entire_pack=entire_pack)
