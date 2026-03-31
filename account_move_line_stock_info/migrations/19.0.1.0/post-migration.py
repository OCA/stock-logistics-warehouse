from odoo import api, SUPERUSER_ID

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {"company_ids": False})

    moves = env["stock.move"].search([])

    for move in moves:
        # Example fix
        if not move.company_id:
            move.company_id = env.company.id