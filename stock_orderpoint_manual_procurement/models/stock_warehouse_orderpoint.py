# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from datetime import datetime
from openerp.addons import decimal_precision as dp
from openerp.tools import float_compare, float_round


UNIT = dp.get_precision('Product Unit of Measure')


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    @api.multi
    @api.depends("product_min_qty", "product_id", "qty_multiple")
    def _compute_procure_recommended(self):
        procurement_model = self.env['procurement.order']
        op_qtys = self.subtract_procurements_from_orderpoints(self.ids)
        for op in self:
            op.procure_recommended_date = \
                procurement_model._get_orderpoint_date_planned(
                    op, datetime.today())
            procure_recommended_qty = 0.0
            prods = op.with_context(
                location=op.location_id.id).product_id.virtual_available
            if prods is None:
                continue
            if float_compare(prods, op.product_min_qty,
                             precision_rounding=op.product_uom.rounding) < 0:
                qty = max(op.product_min_qty, op.product_max_qty) - prods
                reste = op.qty_multiple > 0 and qty % op.qty_multiple or 0.0
                if float_compare(
                        reste, 0.0,
                        precision_rounding=op.product_uom.rounding) > 0:
                    qty += op.qty_multiple - reste

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

    procure_recommended_qty = fields.Float(
        string='Procure recommendation',
        compute="_compute_procure_recommended",
        digits=UNIT)
    procure_recommended_date = fields.Date(
        string='Request Date',
        compute="_compute_procure_recommended")
