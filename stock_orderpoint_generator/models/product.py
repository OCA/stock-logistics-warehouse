# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    auto_orderpoint_template_ids = fields.Many2many(
        comodel_name='stock.warehouse.orderpoint.template',
        string="Automatic Reordering Rules",
        domain=[('auto_generate', '=', True)],
        help="When one or several automatic reordering rule is selected, "
             "a Scheduled Action will automatically generate or update "
             "the reordering rules of the product."
    )

    @api.model
    def create(self, vals):
        record = super(ProductProduct, self).create(vals)
        if vals.get('auto_orderpoint_template_ids'):
            record.auto_orderpoint_template_ids.create_orderpoints(record.ids)
        return record

    @api.multi
    def write(self, vals):
        result = super(ProductProduct, self).write(vals)
        if vals.get('auto_orderpoint_template_ids'):
            orderpoint_templates = self.mapped('auto_orderpoint_template_ids')
            orderpoint_templates.create_orderpoints(self.ids)
        return result
