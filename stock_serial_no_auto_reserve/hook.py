from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    cr.execute("ALTER TABLE stock_move ADD COLUMN is_available BOOLEAN")
    cr.execute("UPDATE stock_move SET is_available = FALSE")


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("SELECT id FROM stock_move WHERE state IN ('waiting', 'confirmed')")
    results = cr.fetchall()
    for result in results:
        move_id = result[0]
        move = env["stock.move"].browse(move_id)
        move._compute_is_available()
        cr.commit()
