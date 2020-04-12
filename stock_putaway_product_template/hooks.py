# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    openupgrade.logged_query(
        cr, """
        UPDATE stock_fixed_putaway_strat sfps
        SET product_tmpl_id=pp.product_tmpl_id
        FROM product_product pp
            WHERE pp.id=sfps.product_id AND
                sfps.product_tmpl_id <> pp.product_tmpl_id
        """
    )
