# Copyright 2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    orders = env["sale.order"].search(
        [("state", "=", "sent"), ("is_stock_reservable", "=", False)]
    )
    orders._compute_stock_reservation()
