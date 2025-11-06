# Copyright 2018 Camptocamp SA
# Copyright 2016 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import logging
from psycopg2 import Error
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = "stock.quant"

    contains_unreserved = fields.Boolean(
        string="Contains unreserved products",
        compute="_compute_contains_unreserved",
        store=True,
    )

    unreserved_quantity = fields.Float(
        string="Unreserved quantity",
        compute="_compute_unreserved_quantity",
        store=True,
    )

    @api.depends('unreserved_quantity')
    def _compute_contains_unreserved(self):
        for record in self:
            record.contains_unreserved = record.unreserved_quantity > 0

    @api.depends('quantity', 'reserved_quantity')
    def _compute_unreserved_quantity(self):
        for rec in self:
            rec.unreserved_quantity = rec.quantity - rec.reserved_quantity

    @api.model
    def _merge_quants(self):
        """ replaces Odoo _merge_quants """
        query = """WITH
                       dupes AS (
                           SELECT min(id) as to_update_quant_id,
                               (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)]
                                   as to_delete_quant_ids,
                               SUM(reserved_quantity) as reserved_quantity,
                               SUM(quantity) as quantity,
                               SUM(unreserved_quantity) as unreserved_quantity
                           FROM stock_quant
                           GROUP BY product_id, company_id, location_id, lot_id,
                               package_id, owner_id, in_date
                           HAVING count(id) > 1
                       ),
                       _up AS (
                           UPDATE stock_quant q
                               SET quantity = d.quantity,
                                   reserved_quantity = d.reserved_quantity,
                                   unreserved_quantity = d.unreserved_quantity
                           FROM dupes d
                           WHERE d.to_update_quant_id = q.id
                       )
                   DELETE FROM stock_quant WHERE id in (
                        SELECT unnest(to_delete_quant_ids) from dupes)
        """
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(query)
        except Error as e:
            _logger.info('An error occurred while merging quants: %s', e.pgerror)
