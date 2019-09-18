
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

from odoo import fields, models, api


class StockConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_consumption_calculation_method(self):
        return [
            ('moves', 'Moves (calculate consumption based on Stock Moves)'),
            ('history', 'Calculate consumption based on the Product History'),
        ]

    default_consumption_calculation_method = fields.Selection(
        _get_consumption_calculation_method,
        'Consumption Calculation Method', default='moves',
        default_model='product.template')
    default_calculation_range = fields.Integer(
        'Calculation Range in days', default=365,
        default_model='product.template', help="""This field is used if the"""
        """ selected method is based on Stock Moves."""
        """Number of days used for"""
        """ the calculation of the average consumption. For example: if you"""
        """ put 365, the calculation will be done on last year.""")
    default_display_range = fields.Integer(
        'Display Range in days', default=1,
        default_model='product.template', help="""Examples:
        1 -> Average Consumption per days
        7 -> Average Consumption per week
        30 -> Average Consumption per month""")
    module_product_history = fields.Boolean(
        "View product History",
        help="This will install product_history module")

    @api.onchange('default_consumption_calculation_method')
    def _onchange_default_consumption_calculation_method(self):
        if self.default_consumption_calculation_method == 'history':
            self.module_product_history = True

    @api.onchange('module_product_history')
    def _onchange_module_product_history(self):
        if not self.module_product_history:
            self.default_consumption_calculation_method = 'moves'

    @api.model
    def create(self, vals):
        if vals.get('default_display_range', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET display_range=%s""", (
                vals.get('default_display_range'),))
        if vals.get('default_calculation_range', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET calculation_range=%s""", (
                vals.get('default_calculation_range'),))
        # TOCHECK Need to move to product_history module
        # if vals.get('default_number_of_periods', False):
        #     self.env.cr.execute("""
        #         UPDATE product_template
        #         SET number_of_periods=%s""", (
        #         vals.get('default_number_of_periods'),))
        if vals.get('default_consumption_calculation_method', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET consumption_calculation_method=%s""", (
                vals.get('default_consumption_calculation_method'),))
        return super(StockConfigSettings, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('default_display_range', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET display_range=%s""", (
                vals.get('default_display_range'),))
        if vals.get('default_calculation_range', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET calculation_range=%s""", (
                vals.get('default_calculation_range'),))
        # TOCHECK Need to move to product_history module
        # if vals.get('default_number_of_periods', False):
        #     self.env.cr.execute("""
        #         UPDATE product_template
        #         SET number_of_periods=%s""", (
        #         vals.get('default_number_of_periods'),))
        if vals.get('default_consumption_calculation_method', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET consumption_calculation_method=%s""", (
                vals.get('default_consumption_calculation_method'),))
        return super(StockConfigSettings, self).write(vals)

    @api.onchange('default_calculation_range')
    @api.multi
    def _onchange_default_calculation_range(self):
        for config in self:
            self.env.cr.execute("""
                UPDATE product_template
                SET calculation_range=%s""", (
                config.default_calculation_range,))
