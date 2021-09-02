# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    if not version:
        return

    env = api.Environment(cr, SUPERUSER_ID, {})
    settings = env["res.config.settings"].search(
        [("group_bypass_submit_request", "=", True)]
    )
    if not settings:
        settings = env["res.config.settings"].create(
            {
                "group_bypass_submit_request": True,
            }
        )
    settings.execute()
