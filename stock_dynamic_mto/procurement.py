# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Benoît GUILLOT <benoit.guillot@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from openerp import models, fields, api


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    mts_pull_rule_id = fields.Many2one('procurement.rule',
                                       string="MTS Rule")


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def get_mto_qty_to_order(self):
        self.ensure_one()
        uom_obj = self.env['product.uom']
        proc_warehouse = self.with_context(warehouse=self.warehouse_id.id)
        virtual_available = proc_warehouse.product_id.virtual_available
        qty_available = uom_obj._compute_qty(self.product_id.uom_id.id,
                                             virtual_available,
                                             self.product_uom.id)
        if qty_available > 0:
            if qty_available >= self.product_qty:
                return 0.0
            else:
                return self.product_qty - qty_available
        return self.product_qty

    @api.model
    def _run(self, procurement):
        uom_obj = self.env['product.uom']
        rule_id = procurement.rule_id
        rule_mts = rule_id and rule_id.mts_pull_rule_id or False
        if rule_mts:
            needed_qty = procurement.get_mto_qty_to_order()
            if needed_qty == 0.0:
                procurement.write({'rule_id': rule_mts.id})
                return super(ProcurementOrder, self)._run(procurement)
            else:
                if needed_qty != procurement.product_qty:
                    mts_qty = procurement.product_qty - needed_qty
                    mts_uos_qty = uom_obj._compute_qty(
                        procurement.product_uom.id,
                        mts_qty,
                        procurement.product_uos.id)
                    default_vals = {
                        'product_qty': mts_qty,
                        'product_uos_qty': mts_uos_qty,
                    }
                    uos_qty = procurement.product_uos_qty
                    update_vals = {
                        'product_qty': needed_qty,
                        'product_uos_qty': uos_qty - mts_uos_qty,
                    }
                    mts_proc = procurement.copy(default=default_vals)
                    mts_proc.run()
                    procurement.write(update_vals)
        return super(ProcurementOrder, self)._run(procurement)
