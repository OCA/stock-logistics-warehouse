#  Copyright 2019 Tecnativa - Sergio Teruel
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    # Remove old security group_uom from product template view because now has
    # a new group for secondary units
    group_uom = env.ref('product.group_uom')
    views = env['ir.ui.view'].browse()
    views += env.ref('stock_secondary_unit.view_template_property_form')
    views += env.ref(
        'stock_secondary_unit.product_template_form_view_procurement_button')
    views += env.ref(
        'stock_secondary_unit.product_form_view_procurement_button')
    views += env.ref('stock_secondary_unit.product_template_tree_view')
    views += env.ref('stock_secondary_unit.product_product_tree_view')
    views += env.ref(
        'stock_secondary_unit.view_stock_move_line_operation_tree')
    views += env.ref('stock_secondary_unit.view_picking_form')

    views.write({
        'groups_id': [(3, group_uom.id)]
    })
