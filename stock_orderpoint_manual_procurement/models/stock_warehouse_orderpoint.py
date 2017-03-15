# -*- coding: utf-8 -*-
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import datetime
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round


UNIT = dp.get_precision('Product Unit of Measure')


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    procure_recommended_qty = fields.Float(
        string='Procure Recommendation',
        compute="_compute_procure_recommended",
        digits=UNIT,
    )
    procure_recommended_date = fields.Date(
        string='Recommended Request Date',
        compute="_compute_procure_recommended",
    )

    @api.multi
    @api.depends("product_min_qty", "product_id", "qty_multiple")
    def _compute_procure_recommended(self):
        op_qtys = self.subtract_procurements_from_orderpoints()
        for op in self:
            op.procure_recommended_date = op._get_date_planned(
                datetime.today())
            procure_recommended_qty = 0.0
            virtual_qty = op.with_context(
                location=op.location_id.id).product_id.virtual_available
            if float_compare(virtual_qty, op.product_min_qty,
                             precision_rounding=op.product_uom.rounding) < 0:
                qty = max(op.product_min_qty, op.product_max_qty) - virtual_qty
                remainder = \
                    op.qty_multiple > 0 and qty % op.qty_multiple or 0.0
                if float_compare(
                        remainder, 0.0,
                        precision_rounding=op.product_uom.rounding) > 0:
                    qty += op.qty_multiple - remainder

                if float_compare(
                        qty, 0.0,
                        precision_rounding=op.product_uom.rounding) <= 0:
                    continue

                qty -= op_qtys[op.id]
                qty_rounded = float_round(
                    qty, precision_rounding=op.product_uom.rounding)
                if qty_rounded > 0:
                    procure_recommended_qty = qty_rounded
                if op.procure_uom_id:
                    product_qty = op.procure_uom_id._compute_qty(
                        op.product_id.uom_id.id, procure_recommended_qty,
                        op.procure_uom_id.id)
                else:
                    product_qty = procure_recommended_qty

                op.procure_recommended_qty = product_qty
