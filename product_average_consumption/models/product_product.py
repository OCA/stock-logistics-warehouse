##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2019-Today: La Louve (<https://cooplalouve.fr>)
#    Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#    @author Druidoo
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Columns Section
    average_consumption = fields.Float(compute="_compute_average_consumption")
    displayed_average_consumption = fields.Float(
        compute="_compute_displayed_average_consumption",
        string="Average Consumption (Range)",
    )
    total_consumption = fields.Float(compute="_compute_average_consumption")
    nb_days = fields.Integer(
        compute="_compute_average_consumption",
        string="Number of days for the calculation",
        help="""The calculation will be done according to Calculation Range"""
        """ field or since the first stock move of the product if it's"""
        """ more recent""",
    )
    consumption_calculation_method = fields.Selection(
        related="product_tmpl_id.consumption_calculation_method"
    )
    display_range = fields.Integer(related="product_tmpl_id.display_range")
    calculation_range = fields.Integer(related="product_tmpl_id.calculation_range")

    @api.depends("consumption_calculation_method", "calculation_range")
    def _compute_average_consumption(self):
        for product in self:
            product.average_consumption = 0.0
            product.total_consumption = 0.0
            product.nb_days = 0
            if product.consumption_calculation_method == "moves":
                product._average_consumption_moves()

    @api.model
    def _min_date(self, product_id):
        read_group_res = self.env["stock.move"]._read_group(
            [("product_id", "=", product_id)],
            ["product_id"],
            ["date:min"],
            limit=1,
        )
        min_date = time.strftime("%Y-%m-%d")
        if read_group_res and isinstance(read_group_res[0][1], datetime):
            min_date = read_group_res[0][1].strftime("%Y-%m-%d")
        return min_date

    def _get_domain_dates(self, from_date=False, to_date=False):
        domain = []
        if from_date:
            domain.append(("date", ">=", from_date))
        if to_date:
            domain.append(("date", "<=", to_date))
        return domain

    def _get_domain_move_out(self):
        dql, dmil, domain_move_out_loc = self._get_domain_locations()
        domain_move_out = [
            ("state", "not in", ("cancel", "draft"))
        ] + domain_move_out_loc

        owner_id = self._context.get("owner_id")
        if owner_id is not None:
            domain_move_out += [("restrict_partner_id", "=", owner_id)]
        return domain_move_out

    def _average_consumption_moves(self):
        self.ensure_one()
        domain_move_out = self._get_domain_move_out()
        self_ids = self.ids
        if not self_ids:
            self.average_consumption = 0.0
            self.total_consumption = 0.0
            self.nb_days = 0
            return
        calculation_range = self.calculation_range
        begin_date = (datetime.today() - timedelta(days=calculation_range)).strftime(
            "%Y-%m-%d"
        )
        first_date = max(begin_date, self._min_date(self_ids[0]))
        domain_move_out_with_date = (
            self._get_domain_dates(first_date)
            + [("product_id", "in", self_ids)]
            + domain_move_out
        )
        moves_out = self.env["stock.move"].read_group(
            domain_move_out_with_date, ["product_id", "product_qty"], ["product_id"]
        )
        moves_out = dict([(x["product_id"][0], x["product_qty"]) for x in moves_out])
        outgoing_qty = float_round(
            moves_out.get(self_ids[0], 0.0),
            precision_rounding=self.uom_id.rounding,
        )
        nb_days = (datetime.today() - datetime.strptime(first_date, "%Y-%m-%d")).days
        self.nb_days = nb_days
        self.total_consumption = outgoing_qty
        self.average_consumption = nb_days and (outgoing_qty / nb_days) or 0.0

    @api.depends("display_range", "average_consumption")
    def _compute_displayed_average_consumption(self):
        for product in self:
            product.displayed_average_consumption = (
                product.average_consumption * product.display_range
            )
