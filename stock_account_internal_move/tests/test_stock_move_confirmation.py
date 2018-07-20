from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools import mute_logger
from psycopg2 import IntegrityError


class StockMoveConfirmationCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # we need to emulate a move from one internal location to another one
        cls.product = cls.env['product.product'].create({
            'name': 'Whatever',
            'type': 'product',
            'uom_id': cls.env.ref('product.product_uom_kgm').id,
            'uom_po_id': cls.env.ref('product.product_uom_kgm').id,
        })
        cls.location_from = cls.env.ref('stock.location_gate_a')
        cls.location_to = cls.env.ref('stock.location_gate_b')
        cls.account_from = cls.env['account.account'].create({
            'name': 'From Location valuation account',
            'code': 'fr0m10c4t10n',
            'user_type_id': cls.env.ref(
                'account.data_account_type_revenue').id,
        })

    def _create_move(self):
        """Create a dummy move from Gate A to Gate B."""
        return self.env['stock.move'].create({
            'location_id': self.location_from.id,
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom': self.product.uom_id.id,
            'location_dest_id': self.location_to.id,
            'move_line_ids': [
                (0, 0, {
                    'product_id': self.product.id,
                    'qty_done': 5,
                    'location_id': self.location_from.id,
                    'location_dest_id': self.location_to.id,
                    'product_uom_id': self.product.uom_id.id,
                }),
            ],
        })

    def test_00_regular_move(self):
        """Ensure that we didn't broke anything completely.

        Regular case, customization shouldn't have any effect on it.
        """
        # ensure that we're running in a regular setup
        self.assertFalse(self.location_from.force_accounting_entries)
        self.assertFalse(self.location_to.force_accounting_entries)
        self.assertFalse(self.location_from.valuation_internal_account_id)
        self.assertFalse(self.location_to.valuation_internal_account_id)
        # then: simple as that - we're just ensuring that we can do that.
        move = self._create_move()
        move._action_done()

    @mute_logger('odoo.sql_db')
    def test_10_constraint(self):
        """Test that it's impossible to force entries w/o an account."""
        with self.assertRaises(IntegrityError):
            self.location_from.write({
                'force_accounting_entries': True,
            })

    def test_20_wrongly_configured_from_location(self):
        """Test behavior when one of locations isn't configured properly.

        I.e., one of those locations doesn't have a valuation account on it:
        while the other does - this should prevent users from creating
        moves between those locations.
        """
        self.location_from.write({
            'force_accounting_entries': True,
            'valuation_internal_account_id': self.account_from.id,
        })
        with self.assertRaises(ValidationError):
            self._create_move()._action_done()

    def test_40_wrongly_configured_to_location(self):
        """Test behavior when one of locations isn't configured properly.

        Same as above, but now it is dest location that is misconfigured.
        """
        self.location_to.write({
            'force_accounting_entries': True,
            'valuation_internal_account_id': self.account_from.id,
        })
        with self.assertRaises(ValidationError):
            self._create_move()._action_done()
