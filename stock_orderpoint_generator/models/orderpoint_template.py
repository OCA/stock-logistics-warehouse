# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models


class OrderpointTemplate(models.Model):
    """ Template for orderpoints

    Here we use same model as stock.warehouse.orderpoint but set product_id
    as non mandatory as we cannot remove it. This field will be ignored.

    This has the advantage of ensuring that the order point
    and the order point template have the same fields.

    _table is redefined to separate templates from orderpoints
    """
    _name = 'stock.warehouse.orderpoint.template'
    _description = 'Reordering Rule Templates'

    _inherit = 'stock.warehouse.orderpoint'
    _table = 'stock_warehouse_orderpoint_template'

    name = fields.Char(copy=True)
    group_id = fields.Many2one(copy=True)

    product_id = fields.Many2one(required=False)
    product_uom = fields.Many2one(required=False)

    auto_generate = fields.Boolean(
        string='Create Rules Automatically',
        help="When checked, the 'Reordering Rule Templates Generator' "
             "scheduled action will automatically update the rules of a "
             "selection of products."
    )
    auto_product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Products',
        help="A reordering rule will be automatically created by the "
             "scheduled action for every product in this list."
    )
    auto_last_generation = fields.Datetime(string='Last Automatic Generation')

    def _disable_old_instances(self, product_ids):
        """ Clean old instance by setting those inactives
        """
        orderpoints = self.env['stock.warehouse.orderpoint'].search(
            [('product_id', 'in', product_ids)]
        )
        orderpoints.write({'active': False})

    def _create_instances(self, product_ids):
        """ Create instances of model using template inherited model
        """
        orderpoint_model = self.env['stock.warehouse.orderpoint']
        for data in self.copy_data():
            data.pop('auto_generate', None)
            data.pop('auto_product_ids', None)
            data.pop('auto_last_generation', None)
            for product_id in product_ids:
                vals = data.copy()
                vals['product_id'] = product_id
                orderpoint_model.create(vals)

    @api.multi
    def create_orderpoints(self, product_ids):
        """ Create orderpoint for *product_ids* based on these templates.

        :type product_ids: list of int
        """
        self._disable_old_instances(product_ids)
        self._create_instances(product_ids)

    @api.multi
    def create_auto_orderpoints(self):
        for template in self:
            if not template.auto_generate:
                continue
            if (not template.auto_last_generation or
                    template.write_date > template.auto_last_generation):
                template.auto_last_generation = fields.Datetime.now()
                template.create_orderpoints(template.auto_product_ids.ids)

    @api.model
    def _cron_create_auto_orderpoints(self):
        self.search([('auto_generate', '=', True)]).create_auto_orderpoints()
