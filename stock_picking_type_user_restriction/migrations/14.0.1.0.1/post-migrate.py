# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_rule(env):
    picking_type_rule = env.ref(
        "stock_picking_type_user_restriction.picking_type_assigned_users"
    )
    picking_rule = env.ref("stock_picking_type_user_restriction.picking_assigned_users")

    picking_type_rule.write({"domain_force": "[('assigned_user_ids','in',user.id)]"})
    picking_rule.write(
        {"domain_force": "[('picking_type_id.assigned_user_ids','in',user.id)]"}
    )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_rule(env)
