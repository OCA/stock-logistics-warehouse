# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

__name__ = u"Store the inventory revaluation in the account move"
_logger = logging.getLogger(__name__)

__name__ = "Upgrade to 8.0.1.1.0"


def set_revaluation_in_account_move(cr):

    cr.execute(
        """
        UPDATE account_move as am
        SET stock_inventory_revaluation_id = sir.id
        FROM stock_inventory_revaluation as sir
        WHERE old_account_move_id = am.id
        """)


def migrate(cr, version):
    if not version:
        return
    set_revaluation_in_account_move(cr)
