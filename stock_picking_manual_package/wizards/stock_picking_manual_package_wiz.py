# Copyright 2022 Sergio Teruel - Tecnativa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPicking(models.TransientModel):
    _name = "stock.picking.manual.package.wiz"
    _description = "Stock picking manual package wizard"

    picking_id = fields.Many2one(comodel_name="stock.picking")
    package_id = fields.Many2one(
        comodel_name="stock.quant.package",
        help="If this field is set, when you click on 'Put in pack' all done quantities "
        "will be include in this package",
    )
    nbr_lines_into_package = fields.Integer(
        string="Number lines to packaging",
        help="If set, the package will be assigned to the N reserved detailed operations",
    )

    def action_confirm(self):
        if not self.package_id:
            return self.picking_id.with_context(skip_manual_package=True).put_in_pack()
        return self.picking_id.with_context(
            put_in_pack_package_id=self.package_id,
            skip_manual_package=True,
            nbr_lines_into_package=self.nbr_lines_into_package,
        ).put_in_pack()
