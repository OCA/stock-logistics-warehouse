# Copyright 2017 Camptocamp SA
# Copyright 2019 David Vidal - Tecnativa
# Copyright 2020 Víctor Martínez - Tecnativa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import OrderedDict
from datetime import timedelta

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    auto_orderpoint_template_ids = fields.Many2many(
        comodel_name="stock.warehouse.orderpoint.template",
        string="Automatic Reordering Rules",
        domain=[("auto_generate", "=", True)],
        help="When one or several automatic reordering rule is selected, "
        "a Scheduled Action will automatically generate or update "
        "the reordering rules of the product.",
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if vals.get("auto_orderpoint_template_ids"):
            record.auto_orderpoint_template_ids.create_orderpoints(record)
        return record

    def write(self, vals):
        result = super().write(vals)
        if vals.get("auto_orderpoint_template_ids"):
            self.auto_orderpoint_template_ids.create_orderpoints(self)
        return result

    def _get_stock_move_domain(self, domain_move=False, from_date=False, to_date=False):
        domain = [("product_id", "in", self.ids), ("state", "=", "done")] + domain_move
        if from_date:
            domain += [("date", ">=", from_date)]
        domain += [("date", "<=", to_date)]
        return domain

    def _set_product_moves_dict(
        self, moves=False, location=False, from_date=False, to_date=False
    ):
        # Obtain a dict with the stock snapshot for the relative date_from
        # otherwise, the first move will counted as first stock value. We
        # default the compute the stock value anyway to default the value
        # for products with no moves for the given period
        initial_stock = {}
        # Compute the second before the given date so we don't duplicate
        # history values in case the given hour is the same than the one
        # of the first move
        from_date_stock = from_date - timedelta(seconds=1)
        to_date_stock = to_date + timedelta(seconds=1)
        initial_stock = self.with_context(location=location)._compute_quantities_dict(
            False, False, False, to_date=from_date_stock or to_date_stock
        )
        product_moves_dict = {}
        for move in moves:
            product_moves_dict.setdefault(move["product_id"][0], {})
            product_moves_dict[move["product_id"][0]].update(
                {move["date"]: {"prod_qty": move["product_qty"]}}
            )
        for product in self.with_context(prefetch_fields=False):
            # If no there are no moves for a product we default the stock
            # to the one for the given period nevermind the dates
            product_moves = product_moves_dict.get(product.id)
            prod_initial_stock = initial_stock.get(product.id, {})
            if not product_moves:
                product_moves_dict[product.id] = {
                    to_date: {
                        "prod_qty": 0,
                        "stock": prod_initial_stock.get("qty_available", 0),
                    },
                    "stock_history": [prod_initial_stock.get("qty_available", 0)],
                }
                continue
            # Now we'll sort the moves by date and assign an initial stock so
            # we can compute the stock historical values from the moves
            # sequence so we can exploit it statisticaly
            product_moves = OrderedDict(sorted(product_moves.items()))
            product_moves_dict[product.id]["stock_history"] = [
                prod_initial_stock.get("qty_available", 0)
            ]
            stock = 0
            first_item = product_moves[next(iter(product_moves))]
            if from_date:
                stock = prod_initial_stock.get("qty_available")
            first_item["stock"] = stock + first_item["prod_qty"]
            stock = first_item["stock"]
            iter_moves = iter(product_moves)
            next(iter_moves, None)
            for date in iter_moves:
                stock += product_moves[date]["prod_qty"]
                product_moves[date]["stock"] = stock
            product_moves_dict[product.id]["stock_history"] += [
                v["stock"] for k, v in product_moves.items()
            ]
        return product_moves_dict

    def _get_delivered_to_customer_dict(
        self, location=False, from_date=False, to_date=False
    ):
        """Returns a dict of products with their delivered qtys for the
        given dates and locations
        """
        domain = [
            ("product_id", "in", self.ids),
            ("state", "=", "done"),
            ("location_dest_id.usage", "=", "customer"),
        ]
        if location:
            domain += [("location_id", "child_of", location.id)]
        if from_date:
            domain += [("date", ">=", from_date)]
        if to_date:
            domain += [("date", "<=", to_date)]
        move_lines = self.env["stock.move.line"].read_group(
            domain, ["product_id", "qty_done"], ["product_id"]
        )
        return {p["product_id"][0]: p["qty_done"] for p in move_lines}

    def _compute_historic_quantities_dict(
        self, location_id=False, from_date=False, to_date=False
    ):
        """Returns a dict of products with a dict of historic moves as for
        a list of historic stock values resulting from those moves. If
        a location_id is passed, we can restrict it to such location"""
        location = location_id and location_id.id
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self.with_context(
            location=location
        )._get_domain_locations()
        if not to_date:
            to_date = fields.Datetime.now()
        domain_move_in = self._get_stock_move_domain(
            domain_move_in_loc, from_date, to_date
        )
        domain_move_out = self._get_stock_move_domain(
            domain_move_out_loc, from_date, to_date
        )
        move_obj = self.env["stock.move"]
        # Positive moves
        moves_in = move_obj.search_read(
            domain_move_in, ["product_id", "product_qty", "date"], order="date asc"
        )
        # We'll convert to negative these quantities to operate with them
        # to obtain the stock snapshot in every moment
        moves_out = move_obj.search_read(
            domain_move_out, ["product_id", "product_qty", "date"], order="date asc"
        )
        for move in moves_out:
            move["product_qty"] *= -1
        # Merge both results and group them by product id as key
        moves = moves_in + moves_out
        return self._set_product_moves_dict(moves, location, from_date, to_date)
