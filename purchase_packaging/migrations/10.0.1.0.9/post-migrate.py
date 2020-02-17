import odoo


def _compute_void_qties(env):
    """
    Update the product_qty with no values.
    Do it in draft not to write and modify existing moves or ...
    Then update with sql
    :param env:
    :return:
    """
    void_purchase_lines = env['purchase.order.line'].search([
        ('product_qty', '=', False)])
    with void_purchase_lines.env.do_in_draft():
        void_purchase_lines._compute_product_qty()
    for line in void_purchase_lines:
        env.cr.execute(
            """
            UPDATE purchase_order_line SET product_qty = %s
            WHERE id = %s
            """,
            (line.product_qty, line.id)
        )


def migrate(cr, version):
    # We recompute possible void values
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    _compute_void_qties(env)
