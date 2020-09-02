# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, exceptions, fields, models


class CubiscanWizard(models.TransientModel):
    """This wizard is used to show a screen showing Cubiscan information

    It is opened in a headless view (no breadcrumb, no menus, fullscreen).
    """

    _name = "cubiscan.wizard"
    _inherit = "barcodes.barcode_events_mixin"
    _description = "Cubiscan Wizard"
    _rec_name = "device_id"

    device_id = fields.Many2one("cubiscan.device", readonly=True)
    product_id = fields.Many2one("product.product", domain=[("type", "=", "product")])
    line_ids = fields.One2many("cubiscan.wizard.line", "wizard_id")

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            to_create = []
            to_create += self._prepare_unit_line()
            to_create += self._prepare_packaging_lines()
            recs = self.env["cubiscan.wizard.line"].create(to_create)
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
        }
        product_dimension_uom = self.product_id.dimensional_uom_id
        cubiscan_mm_uom = self.env.ref(
            "stock_cubiscan.product_uom_mm", raise_if_not_found=False
        )
        if not cubiscan_mm_uom:
            raise exceptions.UserError(
                _(
                    "Cannot find 'mm' Unit of measure, please update "
                    "`stock_cubiscan` module"
                )
            )
        if cubiscan_mm_uom != product_dimension_uom:
            vals.update(
                {
                    "lngth": product_dimension_uom._compute_quantity(
                        self.product_id.product_length, cubiscan_mm_uom
                    ),
                    "width": product_dimension_uom._compute_quantity(
                        self.product_id.product_width, cubiscan_mm_uom
                    ),
                    "height": product_dimension_uom._compute_quantity(
                        self.product_id.product_height, cubiscan_mm_uom
                    ),
                }
            )
        return [vals]

    def _prepare_packaging_lines(self):
        vals_list = []
        packaging_types = self.env["product.packaging.type"].search([])
        for seq, pack_type in enumerate(packaging_types):
            pack = self.env["product.packaging"].search(
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
        # Action to reopen wizard in fullscreen (e.g. after page refresh)
        self.ensure_one()
        res = self.device_id.open_wizard()
        res["res_id"] = self.id
        return res

    def action_search_barcode(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "cubiscan.wizard.barcode",
            "view_mode": "form",
            "name": _("Barcode"),
            "target": "new",
        }

    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        prod = self.env["product.product"].search([("barcode", "=", barcode)])
        self.product_id = prod
        self.onchange_product_id()

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
                cubiscan_mm_uom = self.env.ref(
                    "stock_cubiscan.product_uom_mm", raise_if_not_found=False
                )
                if not cubiscan_mm_uom:
                    raise exceptions.UserError(
                        _(
                            "Cannot find 'mm' Unit of measure, please update "
                            "`stock_cubiscan` module"
                        )
                    )
                product_vals.update(
                    {
                        "product_length": line.lngth,
                        "product_width": line.width,
                        "product_height": line.height,
                        "dimensional_uom_id": cubiscan_mm_uom.id,
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
        action = self.env.ref("stock_cubiscan.action_cubiscan_device_form").read()[0]
        action.update(
            {
                "res_id": self.device_id.id,
                "target": "main",
                "views": [
                    (
                        self.env.ref("stock_cubiscan.view_cubiscan_device_form").id,
                        "form",
                    )
                ],
                "flags": {"headless": False, "clear_breadcrumbs": True},
            }
        )
        return action


class CubiscanWizardLine(models.TransientModel):
    _name = "cubiscan.wizard.line"
    _description = "Cubiscan Wizard Line"
    _order = "sequence"

    wizard_id = fields.Many2one("cubiscan.wizard")
    sequence = fields.Integer()
    name = fields.Char("Packaging", readonly=True)
    qty = fields.Float("Quantity")
    max_weight = fields.Float("Weight (kg)", readonly=True)
    # this is not a typo:
    # https://github.com/odoo/odoo/issues/41353#issuecomment-568037415
    lngth = fields.Integer("Length (mm)", readonly=True)
    width = fields.Integer("Width (mm)", readonly=True)
    height = fields.Integer("Height (mm)", readonly=True)
    volume = fields.Float(
        "Volume (m³)",
        digits=(8, 4),
        compute="_compute_volume",
        readonly=True,
        store=False,
    )
    barcode = fields.Char("GTIN")
    packaging_id = fields.Many2one(
        "product.packaging", string="Packaging (rel)", readonly=True
    )
    packaging_type_id = fields.Many2one("product.packaging.type", readonly=True,)
    required = fields.Boolean(related="packaging_type_id.required", readonly=True)

    @api.depends("lngth", "width", "height")
    def _compute_volume(self):
        for line in self:
            line.volume = (line.lngth * line.width * line.height) / 1000.0 ** 3

    def cubiscan_measure(self):
        self.ensure_one()
        measures = self.wizard_id.device_id.get_measure()
        # measures are a tuple of 2 slots (measure, precision error),
        # we only care about the measure for now
        measures = {
            "lngth": int(measures["length"][0] * 1000),
            "width": int(measures["width"][0] * 1000),
            "height": int(measures["height"][0] * 1000),
            "max_weight": measures["weight"][0],
        }
        self.write(measures)
