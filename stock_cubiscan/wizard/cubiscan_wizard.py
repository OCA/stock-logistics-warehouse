# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class CubiscanWizard(models.TransientModel):
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
                    "length": 0,
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
                            "length": pack.length,
                            "width": pack.width,
                            "height": pack.height,
                            "barcode": pack.barcode,
                            "packaging_id": pack.id,
                            "packaging_type_id": pack_type.id,
                        }
                    )
                to_create.append(vals)
            recs = self.env["cubiscan.wizard.line"].create(to_create)
            self.line_ids = recs
        else:
            self.line_ids = [(5, 0, 0)]

    @api.multi
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

    @api.multi
    def on_barcode_scanned(self, barcode):
        self.ensure_one()
        prod = self.env["product.product"].search([("barcode", "=", barcode)])
        self.product_id = prod
        self.onchange_product_id()

    @api.multi
    def action_save(self):
        self.ensure_one()
        actions = []
        for line in self.line_ids:
            vals = {
                "name": line.name,
                "qty": line.qty,
                "max_weight": line.max_weight,
                "length": line.length,
                "width": line.width,
                "height": line.height,
                "barcode": line.barcode,
                "packaging_type_id": line.packaging_type_id.id,
            }
            pack = line.packaging_id
            if pack:
                actions.append((1, pack.id, vals))
            else:
                actions.append((0, 0, vals))
        self.product_id.packaging_ids = actions

    @api.multi
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
    length = fields.Integer("Length (mm)", readonly=True)
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
    packaging_id = fields.Many2one("product.packaging", readonly=True)
    packaging_type_id = fields.Many2one(
        "product.packaging.type", readonly=True, required=True
    )
    required = fields.Boolean(related="packaging_type_id.required", readonly=True)

    @api.depends("length", "width", "height")
    def _compute_volume(self):
        for line in self:
            line.volume = (line.length * line.width * line.height) / 1000.0 ** 3

    @api.multi
    def cubiscan_measure(self):
        self.ensure_one()
        measures = self.wizard_id.device_id.get_measure()
        measures = {
            k: (v[0] if k in ["length", "width", "height", "weight"] else False)
            for k, v in measures.items()
        }
        weight = measures.pop("weight")
        measures = {k: int(v * 1000) for k, v in measures.items()}
        measures["max_weight"] = weight
        self.write(measures)
