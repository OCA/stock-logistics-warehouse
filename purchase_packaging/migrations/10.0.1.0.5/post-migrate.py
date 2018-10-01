import odoo


def migrate(cr, version):
    # We recompute possible void values
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    void_purchase_lines = env['purchase.order.line'].search([
        ('product_qty', '=', False)])
    void_purchase_lines._compute_product_qty()
