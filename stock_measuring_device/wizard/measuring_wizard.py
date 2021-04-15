# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import api, fields, models


class MeasuringWizard(models.TransientModel):
    _name = "measuring.wizard"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "measuring Wizard"
    _rec_name = "device_id"

    product_id = fields.Many2one("product.product", domain=[("type", "=", "product")])
    line_ids = fields.One2many("measuring.wizard.line", "wizard_id")
    device_id = fields.Many2one("measuring.device", readonly=True)

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            to_create = []
            to_create += self._prepare_unit_line()
            to_create += self._prepare_packaging_lines()
            recs = self.env["measuring.wizard.line"].create(to_create)
            self.line_ids = recs
        else:
            self.line_ids = [(5, 0, 0)]

    def _prepare_unit_line(self):
        vals = {
            "wizard_id": self.id,
            "sequence": 0,
            "name": "Unit",
            "qty": 1,
            "max_weight": self.product_id.weight,
            "lngth": self.product_id.product_length,
            "width": self.product_id.product_width,
            "height": self.product_id.product_height,
            "is_unit_line": True,
        }
        product_dimension_uom = self.product_id.dimensional_uom_id
        mm_uom = self.env.ref("stock_measuring_device.product_uom_mm")
        if mm_uom != product_dimension_uom:
            vals.update(
                {
                    "lngth": product_dimension_uom._compute_quantity(
                        self.product_id.product_length, mm_uom
                    ),
                    "width": product_dimension_uom._compute_quantity(
                        self.product_id.product_width, mm_uom
                    ),
                    "height": product_dimension_uom._compute_quantity(
                        self.product_id.product_height, mm_uom
                    ),
                }
            )
        return [vals]

    def _prepare_packaging_lines(self):
        vals_list = []
        product_packaging = self.env["product.packaging"]
        packaging_types = self.env["product.packaging.type"].search([])
        for seq, pack_type in enumerate(packaging_types):
            pack = product_packaging.search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("packaging_type_id", "=", pack_type.id),
                ],
                limit=1,
            )
            vals = {
                "wizard_id": self.id,
                "sequence": seq + 1,
                "name": pack_type.name,
                "qty": 0,
                "max_weight": 0,
                "lngth": 0,
                "width": 0,
                "height": 0,
                "barcode": False,
                "packaging_type_id": pack_type.id,
            }
            if pack:
                vals.update(
                    {
                        "qty": pack.qty,
                        "max_weight": pack.max_weight,
                        "lngth": pack.lngth,
                        "width": pack.width,
                        "height": pack.height,
                        "barcode": pack.barcode,
                        "packaging_id": pack.id,
                        "packaging_type_id": pack_type.id,
                    }
                )
            vals_list.append(vals)
        return vals_list

    def action_reopen_fullscreen(self):
        self.ensure_one()
        res = self.device_id.open_wizard()
        res["res_id"] = self.id
        return res

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        prod = self.env["product.product"].search([("barcode", "=", barcode)], limit=1)
        self.product_id = prod

    def action_save(self):
        self.ensure_one()
        product_vals = {}
        packaging_ids_list = []
        for line in self.line_ids:
            packaging_type = line.packaging_type_id
            if packaging_type:
                # Handle lines with packaging
                vals = {
                    "name": line.name,
                    "qty": line.qty,
                    "max_weight": line.max_weight,
                    "lngth": line.lngth,
                    "width": line.width,
                    "height": line.height,
                    "barcode": line.barcode,
                    "packaging_type_id": line.packaging_type_id.id,
                }
                pack = line.packaging_id
                if pack:
                    packaging_ids_list.append((1, pack.id, vals))
                else:
                    packaging_ids_list.append((0, 0, vals))
            else:
                # Handle unit line
                mm_uom = self.env.ref("stock_measuring_device.product_uom_mm")
                product_vals.update(
                    {
                        "product_length": line.lngth,
                        "product_width": line.width,
                        "product_height": line.height,
                        "dimensional_uom_id": mm_uom.id,
                        "weight": line.max_weight,
                    }
                )
        product_vals.update({"packaging_ids": packaging_ids_list})
        self.product_id.write(product_vals)
        # Call onchange to update volume on product.product
        self.product_id.onchange_calculate_volume()
        # reload lines
        self.onchange_product_id()

    def action_close(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": self.device_id._name,
            "res_id": self.device_id.id,
            "view_mode": "form",
            "target": "main",
            "flags": {"headless": False, "clear_breadcrumbs": True},
        }

    def reload(self):
        return {
            "type": "ir.actions.act_view_reload",
        }

    def _notify(self, message):
        """Show a gentle notification on the wizard

        We can't use the user set in the current environment because the user
        that attends the screen (that opened the wizard, thus created it) may
        be not the same than the one (artificial user) that scans and submits
        the data, e.g. by using an api call via a controller. We have to send
        this original user in the environment because notify_warning checks
        that you only notify a user which is the same than the one set in
        the environment.
        """
        self.ensure_one()
        self.create_uid.with_user(self.create_uid.id).notify_warning(message=message)
