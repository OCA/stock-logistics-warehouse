# Copyright 2012-2016 Camptocamp SA
# Copyright 2019 Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, fields, models
from statistics import mean, median_high


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
    product_min_qty = fields.Float(required=False)
    product_max_qty = fields.Float(required=False)

    auto_min_qty = fields.Boolean(
        string="Auto Minimum",
        help="Auto compute minimum quantity "
             "per product for a given a date range",
    )
    auto_min_date_start = fields.Datetime()
    auto_min_date_end = fields.Datetime()
    auto_min_qty_criteria = fields.Selection(
        selection=[
            ('max', 'Maximum'),
            ('median', 'Most frequent'),
            ('avg', 'Average'),
            ('min', 'Minimum'),
        ],
        default='max',
        help="Select a criteria to auto compute the minimum",
    )
    auto_max_qty = fields.Boolean(
        string="Auto Maximum",
        help="Auto compute maximum quantity "
             "per product for a given a date range",
    )
    auto_max_qty_criteria = fields.Selection(
        selection=[
            ('max', 'Maximum'),
            ('median', 'Most frequent'),
            ('avg', 'Average'),
            ('min', 'Minimum'),
        ],
        help="Select a criteria to auto compute the maximum",
    )
    auto_max_date_start = fields.Datetime()
    auto_max_date_end = fields.Datetime()
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

    def _template_fields_to_discard(self):
        """In order to create every orderpoint we should pop this template
           customization fields """
        return [
            'auto_generate', 'auto_product_ids', 'auto_last_generation',
            'auto_min_qty', 'auto_min_date_start', 'auto_min_qty_criteria',
            'auto_min_date_end', 'auto_max_date_start', 'auto_max_date_end',
            'auto_max_qty_criteria', 'auto_max_qty',
        ]

    def _disable_old_instances(self, products):
        """Clean old instance by setting those inactives"""
        orderpoints = self.env['stock.warehouse.orderpoint'].search(
            [('product_id', 'in', products.ids)]
        )
        orderpoints.write({'active': False})

    @api.model
    def _get_criteria_methods(self):
        """Allows to extend methods with other statistical aproaches"""
        return {
            'max': max,
            'median': median_high,
            'avg': mean,
            'min': min,
        }

    @api.model
    def _get_product_qty_by_criteria(
            self, products, location_id, from_date, to_date, criteria):
        """Returns a dict with product ids as keys and the resulting
           calculation of historic moves according to criteria"""
        stock_qty_history = products._compute_historic_quantities_dict(
            location_id=location_id,
            from_date=from_date,
            to_date=to_date)
        criteria_methods = self._get_criteria_methods()
        return {x: criteria_methods[criteria](y['stock_history'])
                for x, y in stock_qty_history.items()}

    def _create_instances(self, product_ids):
        """Create instances of model using template inherited model and
           compute autovalues if needed"""
        orderpoint_model = self.env['stock.warehouse.orderpoint']
        for record in self:
            # Flag equality so we compute the values just once
            auto_same_values = (
                record.auto_max_date_start == record.auto_min_date_start
                ) and (
                    record.auto_max_date_end == record.auto_max_date_end
                    ) and (
                        record.auto_max_qty_criteria ==
                        record.auto_min_qty_criteria)
            stock_min_qty = stock_max_qty = {}
            if record.auto_min_qty:
                stock_min_qty = (
                    self._get_product_qty_by_criteria(
                        product_ids,
                        location_id=record.location_id,
                        from_date=record.auto_min_date_start,
                        to_date=record.auto_min_date_end,
                        criteria=record.auto_min_qty_criteria,
                    ))
                if auto_same_values:
                    stock_max_qty = stock_min_qty
            if record.auto_max_qty and not stock_max_qty:
                stock_max_qty = (
                    self._get_product_qty_by_criteria(
                        product_ids,
                        location_id=record.location_id,
                        from_date=record.auto_max_date_start,
                        to_date=record.auto_max_date_end,
                        criteria=record.auto_max_qty_criteria,
                    ))
            for data in record.copy_data():
                for discard_field in self._template_fields_to_discard():
                    data.pop(discard_field)
                for product_id in product_ids:
                    vals = data.copy()
                    vals['product_id'] = product_id.id
                    if record.auto_min_qty:
                        vals['product_min_qty'] = stock_min_qty.get(
                            product_id.id, 0)
                    if record.auto_max_qty:
                        vals['product_max_qty'] = stock_max_qty.get(
                            product_id.id, 0)
                    orderpoint_model.create(vals)

    @api.multi
    def create_orderpoints(self, products):
        """ Create orderpoint for *products* based on these templates.
        :type products: recordset of products
        """
        self._disable_old_instances(products)
        self._create_instances(products)

    @api.multi
    def create_auto_orderpoints(self):
        for template in self:
            if not template.auto_generate:
                continue
            if (not template.auto_last_generation or
                    template.write_date > template.auto_last_generation):
                template.auto_last_generation = fields.Datetime.now()
                template.create_orderpoints(template.auto_product_ids)

    @api.model
    def _cron_create_auto_orderpoints(self):
        self.search([('auto_generate', '=', True)]).create_auto_orderpoints()
