# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def post_init_hook(cr, registry):

    """INIT stock references in acount move line"""
    # FOR stock moves
    cr.execute(
        """
        UPDATE account_move_line aml SET stock_move_id = am.stock_move_id
        FROM account_move am
        WHERE am.id = aml.move_id
        AND am.stock_move_id IS NOT NULL;
    """
    )
