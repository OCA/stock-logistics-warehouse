# -*- coding: utf-8 -*-
# © 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, fields, models

from openerp.exceptions import UserError

_template_register = ['orderpoint_template_id']


class OrderpointGenerator(models.TransientModel):
    """ Wizard defining stock.warehouse.orderpoint configurations for selected
    products. Those configs are generated using templates
    """

    _name = 'stock.warehouse.orderpoint.generator'
    _description = 'Orderpoint Generator'

    orderpoint_template_id = fields.Many2many(
        'stock.warehouse.orderpoint.template',
        rel='order_point_generator_rel',
        string='Reordering Rule Templates'
    )

    @api.multi
    def action_configure(self):
        """ Action to retrieve wizard data and launch creation of items.
        """
        self.ensure_one()

        product_ids = self.env.context.get('active_ids')
        assert product_ids and isinstance(product_ids, list)

        if self.env.context.get('active_model') == 'product.template':
            templates = self.env['product.template'].browse(product_ids)
            product_ids = templates.mapped('product_variant_ids.id')
            if len(product_ids) != len(templates):
                raise UserError(_(
                    'Cannot apply because some of selected '
                    'products has multiple variants.'
                ))

        self.orderpoint_template_id.create_orderpoints(product_ids)
