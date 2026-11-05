# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Compute the secondary quantity of the existing quants.

    It is computed when its column is created, before the quant's secondary
    unit is filled in, so it is left at 0.
    """
    quants = env["stock.quant"].search([("secondary_uom_id", "!=", False)])
    env.add_to_compute(quants._fields["secondary_uom_qty"], quants)
    quants.flush_recordset(["secondary_uom_qty"])
