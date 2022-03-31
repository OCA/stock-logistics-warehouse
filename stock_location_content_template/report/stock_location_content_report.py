# Copyright (C) 2022 Open Source Integrators (https://www.opensourceintegrators.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class LocationContentReport(models.TransientModel):
    _name = "stock.location.content.report"
    _description = "Stock Location Content Report"

    location_id = fields.Many2one("stock.location", string="Location")
    product_id = fields.Many2one("product.product", string="Product")
    expected_qty = fields.Float(string="Expected Quantity")
    current_qty = fields.Float(string="Current Quantity")
    difference = fields.Float(string="Difference")
    done_transfer = fields.Boolean(default=False)
    parent_location_stock = fields.Float(string="Parent Stock")
    picking_id = fields.Many2one("stock.picking", string="Transfer Reference")

    def _get_stock_location_content_reprot_data(self):
        existing_data = self.search([])
        existing_data.unlink()
        quant_obj = self.env["stock.quant"]
        location_ids = self.env["stock.location"].search([("template_id", "!=", None)])
        for location in location_ids:
            for temp_line in location.template_id.line_ids:
                quants = quant_obj.search(
                    [
                        ("product_id", "=", temp_line.product_id.id),
                        ("location_id", "=", location.id),
                    ]
                )
                current_qty = sum(quant.available_quantity for quant in quants)
                parent_quants = quant_obj.search(
                    [
                        ("product_id", "=", temp_line.product_id.id),
                        ("location_id", "=", location.location_id.id),
                    ]
                )
                parent_qty = sum(quant.available_quantity for quant in parent_quants)
                self.create(
                    {
                        "location_id": location.id,
                        "product_id": temp_line.product_id.id,
                        "expected_qty": temp_line.quantity,
                        "current_qty": current_qty,
                        "difference": temp_line.quantity - current_qty,
                        "parent_location_stock": parent_qty,
                    }
                )

        action = self.env.ref(
            "stock_location_content_template.model_stock_location_content_report_action"
        ).read()[0]
        return action

    def create_internal_transfer(self):
        if self.location_id.location_id.usage == "view":
            raise UserError(_("You can't use view type location in transfer."))

        picking_obj = self.env["stock.picking"]
        wh_id = self.location_id.get_warehouse()
        pick_type_id = wh_id.int_type_id

        if self.difference > 0.0:
            location_id = self.location_id.location_id.id
            location_dest_id = self.location_id.id
            product_qty = self.difference
        if self.difference < 0.0:
            location_id = self.location_id.id
            location_dest_id = self.location_id.location_id.id
            product_qty = abs(self.difference)
        picking_id = picking_obj.search(
            [
                ("picking_type_id", "=", pick_type_id.id),
                ("location_id", "=", location_id),
                ("location_dest_id", "=", location_dest_id),
                ("state", "=", "draft"),
            ],
            limit=1,
        )
        move_lines = [
            (
                0,
                0,
                {
                    "name": self.product_id.name,
                    "product_id": self.product_id.id,
                    "product_uom": self.product_id.uom_id.id,
                    "product_uom_qty": product_qty,
                    "picking_type_id": pick_type_id.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                },
            )
        ]
        if not picking_id:
            picking_id = picking_obj.create(
                {
                    "picking_type_id": pick_type_id.id,
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "move_lines": move_lines,
                }
            )
        else:
            picking_id.write({"move_lines": move_lines})
        self.done_transfer = True
        self.picking_id = picking_id.id

    def open_internal_transfer(self):
        return {
            "name": _("Internal Transfer"),
            "res_model": "stock.picking",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "domain": [
                ("id", "=", self.picking_id.id),
            ],
        }
