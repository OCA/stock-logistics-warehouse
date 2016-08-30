# -*- coding: utf-8 -*-
# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


def rename_column(cr):
    cr.execute(
        """
        ALTER TABLE stock_quant
        RENAME COLUMN partner_id TO dest_partner_id
        """)


def migrate(cr, version):
    if not version:
        return
    rename_column(cr)
