# Copyright 2020 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    stock_request_ids = fields.Many2many(
        comodel_name="stock.request",
        string="Stock Requests",
        readonly=True,
    )
    stock_request_count = fields.Integer(
        "Stock Request #", compute="_compute_stock_request_ids"
    )

    @api.depends("stock_request_ids")
    def _compute_stock_request_ids(self):
        for rec in self:
            rec.stock_request_count = len(rec.stock_request_ids)

    def action_view_stock_request(self):
        """
        :return dict: dictionary value for created view
        """
        action = self.env.ref("stock_request.action_stock_request_form").read()[0]

        requests = self.mapped("stock_request_ids")
        if len(requests) > 1:
            action["domain"] = [("id", "in", requests.ids)]
        elif requests:
            action["views"] = [
                (self.env.ref("stock_request.view_stock_request_form").id, "form")
            ]
            action["res_id"] = requests.id
        return action

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        # import pdb
        # pdb.set_trace()
        if production.stock_request_ids:
            allocations = [
                (
                    0,
                    0,
                    {
                        "stock_request_id": request.id,
                        "requested_product_uom_qty": request.product_qty,
                    },
                )
                for request in production.stock_request_ids
            ]
            # filter out by-product finished moves
            move = production.move_finished_ids.filtered(
                lambda x: x.product_id == production.product_id)
            move.write({'allocation_ids': allocations})
        return production
