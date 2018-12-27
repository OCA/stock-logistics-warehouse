# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class InventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    destination_location_id = fields.Many2one(
        related="inventory_id.destination_location_id",
        readonly=True,
    )
    inventory_type = fields.Selection(
        related="inventory_id.inventory_type",
    )

    def _get_move_location_values(self):
        self.ensure_one()
        location_id = self.inventory_id.destination_location_id
        date = self.inventory_id.date
        return {
            'name': ("MOVE:{}:{}".format(
                self.inventory_id.id,
                self.inventory_id.name,
            )),
            'move_line_ids': self._get_move_line_location_values(),
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_id.id,
            'date': date,
        }

    def _get_move_line_location_values(self):
        self.ensure_one()
        location_id = self.inventory_id.destination_location_id
        return [
            (0, 0, {
                'product_id': self.product_id.id,
                'lot_id': self.prod_lot_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': location_id.id,
                'qty_done': self.product_qty,
                'product_uom_id': self.product_uom_id.id,
            })
        ]
