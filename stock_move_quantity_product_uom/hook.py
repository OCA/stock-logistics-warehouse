from odoo.tools.sql import column_exists, create_column


def pre_init_quantity_product_uom(env):
    if not column_exists(env.cr, "stock_move", "quantity_product_uom"):
        create_column(env.cr, "stock_move", "quantity_product_uom", "float8")
    env.cr.execute(
        """
        UPDATE stock_move sm
        SET quantity_product_uom = sm.quantity
        FROM product_product pp
        JOIN product_template pt ON pt.id = pp.product_tmpl_id
        WHERE sm.product_id = pp.id
          AND pt.uom_id = sm.product_uom
        """
    )
    env.cr.commit()
    return True


def post_init_quantity_product_uom(env):
    env["stock.move"].search(
        [("quantity_product_uom", "=", None)]
    )._compute_quantity_product_uom()
    env.cr.commit()
