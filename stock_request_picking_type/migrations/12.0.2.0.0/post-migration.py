# Copyright (C) 2019 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


def migrate(env, version):
    if not version:
        return

    env.execute(
        "UPDATE stock_request_order "
        "SET picking_type_id = ("
        "SELECT id "
        "FROM stock_picking_type "
        "WHERE code = 'stock_request_order') "
        "WHERE picking_type_id IS NULL;"
    )
