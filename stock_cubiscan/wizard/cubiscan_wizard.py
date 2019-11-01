# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class CubiscanWizard(models.TransientModel):
    _name = 'cubiscan.wizard'
    _inherit = 'barcodes.barcode_events_mixin'
    _description = 'Cubiscan Wizard'
    _rec_name = 'device_id'

    PACKAGING_UNITS = ['Unit', 'kfVE', 'DhVE', 'KrVE', 'PAL']

    device_id = fields.Many2one('cubiscan.device', readonly=True)
    product_id = fields.Many2one('product.template')
    line_ids = fields.One2many('cubiscan.wizard.line', 'wizard_id')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            to_create = []
            for seq, name in enumerate(self.PACKAGING_UNITS):
                pack = self.product_id.packaging_ids.filtered(
                    lambda rec: rec.name == name
                )
                vals = {
                    'wizard_id': self.id,
                    'sequence': seq + 1,
                    'name': name,
                }
                if pack:
                    vals.update(
                        {
                            'qty': pack.qty,
                            'max_weight': pack.max_weight,
                            'length': pack.length,
                            'width': pack.width,
                            'height': pack.height,
                            'barcode': pack.barcode,
                        }
                    )
                to_create.append(vals)
            recs = self.env['cubiscan.wizard.line'].create(to_create)
            self.line_ids = [(6, 0, recs.ids)]
        else:
            self.line_ids = [(5, 0, 0)]

    @api.multi
    def action_reopen_fullscreen(self):
        # Action to reopen wizard in fullscreen (e.g. after page refresh)
        self.ensure_one()
        res = self.device_id.open_wizard()
        res['res_id'] = self.id
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
        prod = self.env['product.template'].search([('barcode', '=', barcode)])
        self.product_id = prod
        self.onchange_product_id()

    @api.multi
    def action_save(self):
        self.ensure_one()
        actions = []
        for line in self.line_ids:
            vals = {
                'sequence': line.sequence,
                'name': line.name,
                'qty': line.qty,
                'max_weight': line.max_weight,
                'length': line.length,
                'width': line.width,
                'height': line.height,
                'barcode': line.barcode,
            }
            pack = self.product_id.packaging_ids.filtered(
                lambda rec: rec.name == line.name
            )
            if pack:
                actions.append((1, pack.id, vals))
            else:
                actions.append((0, 0, vals))
        self.product_id.packaging_ids = actions

    @api.multi
    def action_close(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_cubiscan.action_cubiscan_device_form'
        ).read()[0]
        action.update(
            {
                'res_id': self.device_id.id,
                'target': 'main',
                'views': [
                    (
                        self.env.ref(
                            'stock_cubiscan.view_cubiscan_device_form'
                        ).id,
                        'form',
                    )
                ],
                'flags': {'headless': False, 'clear_breadcrumbs': True},
            }
        )
        return action


class CubiscanWizardLine(models.TransientModel):
    _name = 'cubiscan.wizard.line'
    _description = 'Cubiscan Wizard Line'
    _order = 'sequence'

    wizard_id = fields.Many2one('cubiscan.wizard')
    sequence = fields.Integer()
    name = fields.Char("Packaging", readonly=True)
    qty = fields.Float("Quantity")
    max_weight = fields.Float("Weight (kg)", readonly=True)
    length = fields.Integer("Length (mm)", readonly=True)
    width = fields.Integer("Width (mm)", readonly=True)
    height = fields.Integer("Height (mm)", readonly=True)
    volume = fields.Float(
        "Volume (m3)", compute='_compute_volume', readonly=True, store=False
    )
    barcode = fields.Char("GTIN")

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for line in self:
            line.volume = (
                line.length * line.width * line.height
            ) / 1000.0 ** 3

    @api.multi
    def cubiscan_measure(self):
        self.ensure_one()
        measures = self.wizard_id.device_id.get_measure()
        measures = {
            k: (
                v[0] if k in ['length', 'width', 'height', 'weight'] else False
            )
            for k, v in measures.items()
        }
        weight = measures.pop('weight')
        measures = {k: int(v * 1000) for k, v in measures.items()}
        measures['max_weight'] = weight
        self.write(measures)
