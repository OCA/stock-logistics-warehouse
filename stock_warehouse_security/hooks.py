# Copyright 2026  Akretion (https://www.akretion.com).
# @author Sébastien Alix <sebastien.alix@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.base.models.res_users import USER_PRIVATE_FIELDS


def post_load():
    USER_PRIVATE_FIELDS.append("warehouse_ids")
