# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID


def migrate(cr, version):
    # We recompute possible void values
    env = api.Environment(cr, SUPERUSER_ID, {})
    void_purchase_lines = env['purchase.order.line'].search([
        ('product_qty', '=', False)])
    void_purchase_lines._compute_product_qty()
