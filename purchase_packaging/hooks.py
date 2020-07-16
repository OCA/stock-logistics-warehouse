# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def post_init_hook(cr, registry):
    cr.execute(
        """
        UPDATE purchase_order_line
        SET product_purchase_qty = product_qty
        WHERE product_qty IS NOT NULL"""
    )
