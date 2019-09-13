# -*- coding: utf-8 -*-

from openerp import fields, models, api


class PurchaseConfigSettings(models.TransientModel):
    _inherit = 'stock.config.settings'

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
                SET display_range=%i""" % (
                vals.get('default_display_range')))
        if vals.get('default_calculation_range', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET calculation_range=%i""" % (
                vals.get('default_calculation_range')))
        if vals.get('default_number_of_periods', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET number_of_periods=%i""" % (
                vals.get('default_number_of_periods')))
        if vals.get('default_consumption_calculation_method', False):
            self.env.cr.execute("""
                UPDATE product_template
                SET consumption_calculation_method='%s'""" % (
                vals.get('default_consumption_calculation_method')))
        return super(PurchaseConfigSettings, self).create(vals)

    @api.multi
    def write(self, vals):
        for config in self:
            if vals.get('default_display_range', False):
                self.env.cr.execute("""
                    UPDATE product_template
                    SET display_range=%i""" % (
                    vals.get('default_display_range')))
            if vals.get('default_calculation_range', False):
                self.env.cr.execute("""
                    UPDATE product_template
                    SET calculation_range=%i""" % (
                    vals.get('default_calculation_range')))
            if vals.get('default_number_of_periods', False):
                self.env.cr.execute("""
                    UPDATE product_template
                    SET number_of_periods=%i""" % (
                    vals.get('default_number_of_periods')))
            if vals.get('default_consumption_calculation_method', False):
                self.env.cr.execute("""
                    UPDATE product_template
                    SET consumption_calculation_method='%s'""" % (
                    vals.get('default_consumption_calculation_method')))
        return super(PurchaseConfigSettings, self).write(vals)

    @api.onchange('default_calculation_range')
    @api.multi
    def _onchange_default_calculation_range(self):
        for config in self:
            self.env.cr.execute("""
                UPDATE product_template
                SET calculation_range=%i""" % (
                config.default_calculation_range))
