# Copyright 2013 Camptocamp SA - Guewen Baconnier
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from . import models
from . import wizard
from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    cr.execute("Alter table sale_order add column has_stock_reservation boolean")
    cr.execute("Update sale_order set has_stock_reservation = false")
    cr.execute("Alter table sale_order add column is_stock_reservable boolean")
    cr.execute("Update sale_order set is_stock_reservable = false")


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["sale.order"].search(
        [("state", "in", ["draft", "sent"])]
    )._compute_stock_reservation()
