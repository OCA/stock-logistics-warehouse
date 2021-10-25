# Copyright 2020 Camptocamp
# Copyright 2021 Coop IT Easy SCRL fs
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import logging
from collections import defaultdict
from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)
_QUERY = """
WITH product AS
         (
             SELECT DISTINCT product_id
             FROM stock_move
             WHERE state = 'done'
             AND create_date > %(start_date)s
         ),
     location AS (SELECT id AS location_id, usage FROM stock_location),
     error_move_lines AS (
         SELECT *
         FROM (
                  SELECT sml.id,
                         ROW_NUMBER() OVER (PARTITION BY move_id) as row,
                         sml.qty_done
                  FROM stock_move_line sml
                           JOIN stock_move sm
                                ON sm.id = sml.move_id
                  WHERE sm.inventory_id IS NOT NULL
                    AND sm.state = 'done'
                    AND sm.product_uom_qty < (
                      SELECT SUM(qty_done)
                      FROM stock_move_line sml2
                      WHERE sml2.move_id = sm.id
                      GROUP BY sml2.move_id
                  )
              ) duplicates
         WHERE duplicates.row > 1)
SELECT product_id,
       location_dest_id  AS location_id,
       usage,
       package_id,
       result_package_id as result_package_id,
       SUM(qty_done)     AS qty
FROM stock_move_line sml
         NATURAL JOIN product
         JOIN location ON (location_dest_id = location.location_id)
WHERE state = 'done'
  and sml.id NOT IN (SELECT id FROM error_move_lines)
GROUP BY product_id, location_dest_id, usage, package_id, result_package_id
UNION ALL
SELECT product_id,
       sml.location_id,
       usage,
       package_id,
       result_package_id,
       - SUM(qty_done) AS qty
FROM stock_move_line sml
         NATURAL JOIN product
         JOIN location ON (sml.location_id = location.location_id)
WHERE state = 'done'
  AND sml.id NOT IN (SELECT id FROM error_move_lines)
GROUP BY product_id, sml.location_id, usage, package_id, result_package_id
"""


class AlignMoveQuantWizard(models.Model):
    _name = "align.move.quant.wizard"
    _description = "Align moves and quants"

    @api.model
    def _default_start_date(self):
        """First ever stock move line"""
        first_move_line = self.env["stock.move.line"].search(
            [], order="create_date", limit=1
        )
        if first_move_line:
            return fields.Datetime.to_string(first_move_line.create_date)
        else:
            return False

    start_date = fields.Date(
        string="Start Date",
        required=True,
        default=_default_start_date,
        help="""Date from which to fix the stocks. Either the start in
        version 12 or the first stock move (default value).""",
    )

    @api.multi
    def _fetch_quantities_to_fix(self):
        self.env.cr.execute(_QUERY, {"start_date": self.start_date})
        quantities = defaultdict(int)
        for (
            product_id,
            location_id,
            usage,
            package_id,
            result_package_id,
            qty,
        ) in self.env.cr.fetchall():
            if usage != "internal":
                continue
            if qty < 0:  # when we remove, we may put in a pack
                key = product_id, location_id, usage, package_id
            else:
                key = product_id, location_id, usage, result_package_id
            quantities[key] += qty

        return quantities

    @api.multi
    def _create_fixing_inventory(self):
        quantities = self._fetch_quantities_to_fix()
        inventory = self.env["stock.inventory"].create(
            {
                "name": "Fix stock wizard %s" % datetime.now(),
                "filter": "partial",
                "state": "confirm",
            }
        )
        for (
            product_id,
            location_id,
            _usage,
            package_id,
        ), qty in quantities.items():
            product = self.env["product.product"].browse(product_id)
            package = self.env["stock.quant.package"].browse(package_id)
            location = self.env["stock.location"].browse(location_id)
            quants = (
                self.env["stock.quant"]
                .sudo()
                ._gather(product, location, package_id=package, strict=True)
            )
            actual_qty = sum(quants.mapped("quantity"))
            rounding = product.uom_id.rounding
            if float_compare(qty, actual_qty, precision_rounding=rounding) > 0:
                # create inventory line
                line = self.env["stock.inventory.line"].create(
                    {
                        "inventory_id": inventory.id,
                        "product_id": product_id,
                        "package_id": package_id,
                        "location_id": location_id,
                        "product_uom_id": product.uom_id.id,
                        "product_qty": qty,
                    }
                )
                self.env["stock.quant"].sudo()._update_available_quantity(
                    product, location, qty - actual_qty, package_id=package
                )
                line._compute_theoretical_qty()
                _logger.info(
                    "Product %s in location %s (package: %s): updated qty "
                    "from %.1f to %.1f "
                    % (
                        product.display_name,
                        location.display_name,
                        package.name,
                        actual_qty,
                        qty,
                    )
                )

        if not inventory.line_ids:
            raise UserError(_("No discrepancies found betwen stock moves and quants."))
        return inventory

    def align_move_quant(self):
        _logger.info("fixing stock level: start")
        inventory = self._create_fixing_inventory()
        _logger.info("fixing stock level: end")

        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.inventory",
            "view_type": "form",
            "view_mode": "form",
            "target": "current",
            "res_id": inventory.id,
        }
