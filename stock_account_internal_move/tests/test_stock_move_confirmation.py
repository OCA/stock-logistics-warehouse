from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools import mute_logger


class StockMoveConfirmationCase(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # we need to emulate a move from one internal location to another one
        cls.product = cls.env['product.product'].create({
            'name': 'Whatever',
            'type': 'product',
            'uom_id': cls.env.ref('uom.product_uom_kgm').id,
            'uom_po_id': cls.env.ref('uom.product_uom_kgm').id,
            'standard_price': 100.,
            'valuation': 'real_time',
        })
        cls.location_from = cls.env.ref('stock.location_gate_a')
        cls.location_to = cls.env.ref('stock.location_gate_b')
        cls.location_from.usage = cls.location_to.usage = 'internal'
        account_type_revenue_id = cls.env.ref(
            'account.data_account_type_revenue').id

        cls.account_from_in = cls.env['account.account'].create({
            'name': 'From Location valuation account',
            'code': 'fr0m10c4t10n-1n',
            'user_type_id': account_type_revenue_id,
        })
        cls.account_to_in = cls.env['account.account'].create({
            'name': 'To Location valuation account',
            'code': 't010c4t10n-1n',
            'user_type_id': account_type_revenue_id,
        })
        cls.account_from_out = cls.env['account.account'].create({
            'name': 'From Location valuation account',
            'code': 'fr0m10c4t10n-0u7',
            'user_type_id': account_type_revenue_id,
        })
        cls.account_to_out = cls.env['account.account'].create({
            'name': 'To Location valuation account',
            'code': 't010c4t10n-0u7',
            'user_type_id': account_type_revenue_id,
        })
        cls.location_from.write({
            'force_accounting_entries': True,
            'valuation_in_account_id': cls.account_from_in.id,
            'valuation_out_account_id': cls.account_from_out.id,
        })
        cls.location_to.write({
            'force_accounting_entries': True,
            'valuation_in_account_id': cls.account_to_in.id,
            'valuation_out_account_id': cls.account_to_out.id,
        })
        cls.fake_stock_journal = cls.env['account.journal'].create({
            'name': 'Stock journal (that\'s **not really true)',
            'code': '7h47\'5-n07-|?3411y-7|?u3',
            'type': 'general',
        })

    def _create_move(self):
        """Create a dummy move from Gate A to Gate B."""
        res = self.env['stock.move'].create({
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
            'picking_type_id': self.env.ref('stock.picking_type_internal').id,
        })
        # FIXME: refuses to play well w/ moves w/o picking_id
        # res._assign_picking(self.env.ref('stock.picking_type_internal'))
        res._assign_picking()
        return res

    def test_00_regular_move(self):
        """Ensure that we didn't broke anything completely.

        Regular case, customization shouldn't have any effect on it.
        """
        # ensure that we're running in a regular setup
        self.location_from.force_accounting_entries = False
        self.location_to.force_accounting_entries = False
        # simple as that - we're just ensuring that we're allowed to do it.
        self._create_move()

    @mute_logger('odoo.sql_db')
    def test_10_constraint(self):
        """Test that it's impossible to force entries w/o an account."""
        with self.assertRaises(ValidationError):
            self.location_from.write({
                'force_accounting_entries': True,
                'valuation_in_account_id': False,
            })

    def test_50_create_account_move_line(self):
        move = self._create_move()
        move._action_done()
        # perform a manual evaluation of teh fresh move
        # we don't really care about those numbers
        move._create_account_move_line(
            self.location_from.valuation_out_account_id.id,
            self.location_to.valuation_in_account_id.id,
            self.fake_stock_journal.id)
