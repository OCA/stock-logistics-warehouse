# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


def pre_init_hook(cr):
    cr.execute(
        """ALTER TABLE stock_quant
    ADD COLUMN adjustment_cost numeric
    DEFAULT 0"""
    )

    cr.execute(
        """ALTER TABLE stock_quant
    ALTER COLUMN adjustment_cost DROP DEFAULT;"""
    )
