from odoo import fields, models


class ProductHistorySettings(models.TransientModel):
    _inherit = 'res.config.settings'

    default_history_range = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Week'),
        ('months', 'Month'),
    ],
        'Product History Display Range',
        default='weeks',
        default_model='product.product')

    default_number_of_periods = fields.Integer(
        'Number of valid history periods used for the calculation',
        default=6,
        default_model='product.template',
        help="""This field is used if the selected method is based on"""
             """ Product History""")
