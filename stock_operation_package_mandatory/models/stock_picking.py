# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def _check_mandatory_packages(self):
        """ Check package existence for qty_done operations > 0
        """
        for picking in self:
            if picking.picking_type_id.destination_package_mandatory:
                operations = picking.pack_operation_product_ids.filtered(
                    lambda o: float_compare(
                        o.qty_done,
                        0,
                        o.product_id.uom_id.rounding) > 0)
                if not all([operation.result_package_id
                            for operation in operations]):
                    raise UserError(
                        _('Some Operations do not contain destination'
                          'packages'))

    @api.multi
    def do_new_transfer(self):
        for picking in self:
            picking._check_mandatory_packages()
        return super(StockPicking, self).do_new_transfer()
