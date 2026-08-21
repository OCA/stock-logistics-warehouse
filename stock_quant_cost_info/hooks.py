# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    cr = env.cr
    cr.execute(
        """ALTER TABLE stock_quant
    ADD COLUMN IF NOT EXISTS adjustment_cost numeric
    DEFAULT 0"""
    )
    cr.execute(
        """ALTER TABLE stock_quant
    ALTER COLUMN adjustment_cost DROP DEFAULT;"""
    )
