# Copyright 2019 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAccountMoveLineStockInfo(TransactionCase):
    def test_account_move_line_stock_move_fields(self):
        """Test that the stock_move_id field exists on account.move.line."""
        # Verify the field exists and is properly defined
        aml_model = self.env["account.move.line"]
        self.assertTrue(hasattr(aml_model, "stock_move_id"))

    def test_stock_move_account_move_line_ids(self):
        """Test that the account_move_line_ids field exists on stock.move."""
        # Verify the field exists and is properly defined
        move_model = self.env["stock.move"]
        self.assertTrue(hasattr(move_model, "account_move_line_ids"))
