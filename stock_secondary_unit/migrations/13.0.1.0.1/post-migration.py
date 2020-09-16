# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    # Delete old security group for views.
    views = [
        "stock_secondary_unit.view_template_property_form",
        "stock_secondary_unit.product_template_form_view_procurement_button",
        "stock_secondary_unit.product_form_view_procurement_button",
        "stock_secondary_unit.product_template_tree_view",
        "stock_secondary_unit.product_product_tree_view",
    ]
    IrUiView = env["ir.ui.view"]
    user_group = env.ref("uom.group_uom")
    views_to_update = IrUiView.browse()
    for view in views:
        views_to_update |= env.ref(view)
    views_to_update.write({"groups_id": [(3, user_group.id)]})
