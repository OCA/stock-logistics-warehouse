# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import api, fields, models, _


class ProductCategory(models.Model):

    _inherit = 'product.category'

    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'category_id',
                                       'Putaway Rules')


class ProductProduct(models.Model):

    _inherit = 'product.product'

    putaway_rule_ids = fields.One2many('stock.putaway.rule', 'product_id',
                                       'Putaway Rules')

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            '|',
                ('product_id', '=', self.id),
                ('category_id', '=', self.product_tmpl_id.categ_id.id),
        ]
        return self.env['product.template']._get_action_view_related_putaway_rules(domain)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.model
    def _get_action_view_related_putaway_rules(self, domain):
        return {
            'name': _('Putaway Rules'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.putaway.rule',
            'view_mode': 'list',
            'domain': domain,
        }

    def action_view_related_putaway_rules(self):
        self.ensure_one()
        domain = [
            '|',
                ('product_id.product_tmpl_id', '=', self.id),
                ('category_id', '=', self.categ_id.id),
        ]
        return self._get_action_view_related_putaway_rules(domain)
