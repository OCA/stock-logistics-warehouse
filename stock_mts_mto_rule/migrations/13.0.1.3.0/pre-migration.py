# Copyright 2021 Tecnativa David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Now the record is declared as noupdate
    openupgrade.set_xml_ids_noupdate_value(
        env, "stock_mts_mto_rule", ["route_mto_mts"], True,
    )
