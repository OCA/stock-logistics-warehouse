# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade


def migrate_inventory_revaluation(env):
    revaluations = env['stock.inventory.revaluation'].search([])
    for revaluation in revaluations:
        product_variants = revaluation.product_template_id.\
            with_context(active_test=False).product_variant_ids.mapped('id')
        if revaluation.product_template_id and\
                revaluation.product_template_id.product_variant_count > 1:
            for product_id in product_variants[1:]:
                new_revaluation = revaluation.\
                    copy(default={'product_id': product_id,
                                  'state': 'posted',
                                  'account_move_id': revaluation.
                                  account_move_id.id})
                quants = env['stock.inventory.revaluation.quant'].\
                    search([('product_id', '=', product_id),
                            ('revaluation_id', '=', revaluation.id)])
                if quants:
                    quants.write({'revaluation_id': new_revaluation.id})
        if product_variants:
            prod_dict = {'product_id': product_variants[0]}
            revaluation.write(prod_dict)


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    migrate_inventory_revaluation(env)
