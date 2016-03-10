# -*- coding: utf-8 -*-
###############################################################################
#
#    Module for OpenERP
#    Copyright (C) 2015 Akretion (http://www.akretion.com). All Rights Reserved
#    @author Florian DA COSTA <florian.dacosta@akretion.com>
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
from openerp import models, api, fields


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    mts_mto_procurement_id = fields.Many2one(
        'procurement.order',
        string="Mto+Mts Procurement",
        copy=False)
    mts_mto_procurement_ids = fields.One2many(
        'procurement.order',
        'mts_mto_procurement_id',
        string="Procurements")

    @api.multi
    def get_mto_qty_to_order(self):
        self.ensure_one()
        uom_obj = self.env['product.uom']
        stock_location = self.warehouse_id.lot_stock_id.id
        proc_warehouse = self.with_context(location=stock_location)
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
    def _get_mts_mto_procurement(self, proc, rule, qty, uos_qty):
        origin = (proc.group_id and (proc.group_id.name + ":") or "") + \
                 (proc.rule_id and proc.rule_id.name or proc.origin or "/")
        return {
            'name': proc.name,
            'origin': origin,
            'product_qty': qty,
            'product_uos_qty': uos_qty,
            'rule_id': rule.id,
            'mts_mto_procurement_id': proc.id,
        }

    @api.model
    def _check(self, procurement):
        if procurement.rule_id and \
                procurement.rule_id.action == 'split_procurement':
            cancel_proc_list = [x.state == 'cancel'
                                for x in procurement.mts_mto_procurement_ids]
            done_cancel_test_list = [
                x.state in ('done', 'cancel')
                for x in procurement.mts_mto_procurement_ids]
            if all(cancel_proc_list):
                procurement.write({'state': 'cancel'})
            elif all(done_cancel_test_list):
                return True
        return super(ProcurementOrder, self)._check(procurement)

    @api.multi
    def check(self, autocommit=False):
        res = super(ProcurementOrder, self).check(autocommit=autocommit)
        for procurement in self:
            if procurement.mts_mto_procurement_id:
                procurement.mts_mto_procurement_id.check(
                    autocommit=autocommit)
        return res

    @api.model
    def _run(self, procurement):
        if procurement.rule_id and \
                procurement.rule_id.action == 'split_procurement':
            if procurement.mts_mto_procurement_ids:
                return super(ProcurementOrder, self)._run(procurement)
            uom_obj = self.env['product.uom']
            needed_qty = procurement.get_mto_qty_to_order()
            rule = procurement.rule_id
            if needed_qty == 0.0:
                mts_vals = self._get_mts_mto_procurement(
                    procurement, rule.mts_rule_id, procurement.product_qty,
                    procurement.product_uos_qty)
                mts_proc = procurement.copy(mts_vals)
                mts_proc.run()
            elif needed_qty == procurement.product_qty:
                mto_vals = self._get_mts_mto_procurement(
                    procurement, rule.mto_rule_id, procurement.product_qty,
                    procurement.product_uos_qty)
                mto_proc = procurement.copy(mto_vals)
                mto_proc.run()
            else:
                mts_qty = procurement.product_qty - needed_qty
                mts_uos_qty = uom_obj._compute_qty(
                    procurement.product_uom.id,
                    mts_qty,
                    procurement.product_uos.id)
                mts_vals = self._get_mts_mto_procurement(
                    procurement, rule.mts_rule_id, mts_qty, mts_uos_qty)
                mts_proc = procurement.copy(mts_vals)
                mts_proc.run()

                uos_qty = procurement.product_uos_qty
                mto_vals = self._get_mts_mto_procurement(
                    procurement, rule.mto_rule_id, needed_qty,
                    uos_qty - mts_uos_qty)

                mto_proc = procurement.copy(mto_vals)
                mto_proc.run()
        return super(ProcurementOrder, self)._run(procurement)
