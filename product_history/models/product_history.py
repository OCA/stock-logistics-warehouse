#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    Copyright (C) 2020-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import models, fields, api

HISTORY_RANGE = [
    ('days', 'Days'),
    ('weeks', 'Week'),
    ('months', 'Month'),
]


class ProductHistory(models.Model):
    _name = "product.history"
    _description = "Product History"
    _order = 'from_date desc'

    # Columns section
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product',
        required=True, ondelete='cascade')
    company_id = fields.Many2one(
        'res.company', related='product_id.company_id')
    product_tmpl_id = fields.Many2one(
        'product.template', related='product_id.product_tmpl_id',
        string='Template', store=True)
    location_id = fields.Many2one(
        'stock.location', string='Location', required=True,
        ondelete='cascade')
    from_date = fields.Date(required=True)
    to_date = fields.Date(required=True)
    purchase_qty = fields.Float("Purchases", default=0)
    production_qty = fields.Float("Production", default=0)
    sale_qty = fields.Float("Sales", default=0)
    loss_qty = fields.Float("Losses", default=0)
    start_qty = fields.Float("Opening quantity", default=0)
    end_qty = fields.Float("Closing quantity", default=0)
    incoming_qty = fields.Float("Incoming quantity", default=0)
    outgoing_qty = fields.Float("Outgoing quantity", default=0)
    virtual_qty = fields.Float("Virtual quantity", default=0)
    ignored = fields.Boolean(default=False)
    history_range = fields.Selection(
        HISTORY_RANGE,
        required=True)

    _sql_constraints = [
        ('history_uniq',
         'unique(product_id, location_id, from_date, to_date, history_range)',
         'This history line already exists!'
         ),
    ]

    # Private section
    @api.multi
    def mark_line(self, ignored=True):
        for line in self:
            line.ignored = ignored
            line.product_id._compute_average_consumption()
            line.product_id.product_tmpl_id._compute_average_consumption()

    @api.multi
    def ignore_line(self):
        self.mark_line(True)
        return True

    @api.multi
    def unignore_line(self):
        self.mark_line(False)

    @api.model
    def create(self, vals):
        if vals.get('history_range') == 'weeks' and \
                vals.get('sale_qty', 0) == 0:
            vals['ignored'] = True
        return super(ProductHistory, self).create(vals)
