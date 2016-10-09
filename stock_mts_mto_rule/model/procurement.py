# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
        stock_location = self.warehouse_id.lot_stock_id.id
        proc_warehouse = self.with_context(location=stock_location)
        virtual_available = proc_warehouse.product_id.virtual_available
        qty_available = self.product_id.uom_id._compute_quantity(
            virtual_available, self.product_uom)

        if qty_available > 0:
            if qty_available >= self.product_qty:
                return 0.0
            else:
                return self.product_qty - qty_available
        return self.product_qty

    @api.multi
    def _get_mts_mto_procurement(self, rule, qty):
        self.ensure_one()
        origin = (self.group_id and (self.group_id.name + ":") or "") + \
                 (self.rule_id and self.rule_id.name or self.origin or "/")
        return {
            'name': self.name,
            'origin': origin,
            'product_qty': qty,
            'rule_id': rule.id,
            'mts_mto_procurement_id': self.id,
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

    @api.multi
    def _run(self):
        self.ensure_one()
        if self.rule_id and self.rule_id.action == 'split_procurement':
            if self.mts_mto_procurement_ids:
                return super(ProcurementOrder, self)._run()
            needed_qty = self.get_mto_qty_to_order()
            rule = self.rule_id
            if needed_qty == 0.0:
                mts_vals = self._get_mts_mto_procurement(
                    rule.mts_rule_id, self.product_qty)
                mts_proc = self.copy(mts_vals)
                mts_proc.run()
            elif needed_qty == self.product_qty:
                mto_vals = self._get_mts_mto_procurement(
                    rule.mto_rule_id, self.product_qty)
                mto_proc = self.copy(mto_vals)
                mto_proc.run()
            else:
                mts_qty = self.product_qty - needed_qty
                mts_vals = self._get_mts_mto_procurement(
                    rule.mts_rule_id, mts_qty)
                mts_proc = self.copy(mts_vals)
                mts_proc.run()

                mto_vals = self._get_mts_mto_procurement(
                    rule.mto_rule_id, needed_qty)
                mto_proc = self.copy(mto_vals)
                mto_proc.run()

        return super(ProcurementOrder, self)._run()
