# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict


def post_init_hook(env):
    def get_profile(route_ids):
        route_ids = tuple(set(route_ids))
        profile = route2profile.get(route_ids)
        if not profile:
            profile_name = ""
            route_names = [rec.name for rec in env["stock.route"].browse(route_ids)]
            profile_name = " / ".join(route_names)
            profile = env["route.profile"].create(
                {
                    "name": profile_name,
                    "route_ids": [(6, 0, route_ids)],
                }
            )
            route2profile[route_ids] = profile
        return profile

    query = """
    SELECT product_id, array_agg(route_id)
    FROM stock_route_product group by product_id;
    """
    env.cr.execute(query)
    results = env.cr.fetchall()
    route2profile = {}
    profile2product = defaultdict(lambda: env["product.template"])
    for row in results:
        profile = get_profile(row[1])
        profile2product[profile.id] |= env["product.template"].browse(row[0])

    for profile in profile2product:
        profile2product[profile].write({"route_profile_id": profile})
