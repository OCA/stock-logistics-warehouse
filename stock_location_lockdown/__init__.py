# Copyright 2018 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models


def pre_init_hook(env):
    """Create the outbound reservation lock columns with a SQL default so the
    existing (potentially huge) stock_quant table is initialised in one pass,
    instead of the ORM filling the default row by row when the fields are
    loaded."""
    env.cr.execute(
        """
        ALTER TABLE stock_quant
        ADD COLUMN IF NOT EXISTS lock_real_reserved double precision DEFAULT 0.0;
        ALTER TABLE stock_quant
        ADD COLUMN IF NOT EXISTS is_outbound_reservation_locked boolean
            DEFAULT false;
        """
    )
