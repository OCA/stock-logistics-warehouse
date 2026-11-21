# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>


def post_init_hook(env):
    warehouses = env["stock.warehouse"].search([])
    mto_routes = warehouses.mto_pull_id.route_id
    mto_routes.is_mto = True
