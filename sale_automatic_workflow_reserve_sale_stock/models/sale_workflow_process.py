# -*- coding: utf-8 -*-
# © 2016 FactorLibre - Hugo Santos <hugo.santos@factorlibre.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields


class SaleWorkflowProcess(models.Model):
    _inherit = 'sale.workflow.process'

    stock_reservation = fields.Boolean(
        'Stock Reservation',
        help='Allows to make stock reservations before the confirm the '
             'sale quotation')
    stock_reservation_validity = fields.Integer(
        'Stock Reservation Validity (Days)',
        help='Make a stock reservation for this number of days. '
             'When this number of days pass the stock reservation is released',
        default=5)
    stock_reservation_location_id = fields.Many2one(
        'stock.location',
        'Stock reservation Source Location')
    stock_reservation_location_dest_id = fields.Many2one(
        'stock.location',
        'Stock reservation Location')
