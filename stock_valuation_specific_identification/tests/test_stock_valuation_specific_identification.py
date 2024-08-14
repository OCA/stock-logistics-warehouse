# Copyright 2024 Matt Taylor
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)


@tagged("-at_install", "post_install")
class TestValuationSpecificIdentification(ValuationReconciliationTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # disable tracking to speed up the tests
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.ref("base.main_company")
        cls.cost_account_id = cls.env.ref("l10n_generic_coa.1_cost_of_goods_sold")

        cls.quant_model = cls.env["stock.quant"]
        cls.move_model = cls.env["stock.move.line"]
        cls.location_model = cls.env["stock.location"]

        cls.company_data.update(
            {
                "default_account_stock_cost": cls.env["account.account"].create(
                    {
                        "name": "default_account_stock_cost",
                        "code": "STOCKCOST",
                        "reconcile": True,
                        "account_type": "asset_current",
                        "company_id": cls.company_data["company"].id,
                    }
                )
            }
        )

        cls.product_categ = cls.env["product.category"].create(
            {
                "name": "Test Categ",
                "property_cost_method": "fifo",
                "property_valuation": "real_time",
                "property_specific_ident_cost": True,
                "property_stock_valuation_account_id": cls.company_data[
                    "default_account_stock_valuation"
                ].id,
                "property_stock_account_input_categ_id": cls.company_data[
                    "default_account_stock_in"
                ].id,
                "property_stock_account_output_categ_id": cls.company_data[
                    "default_account_stock_out"
                ].id,
            }
        )
        cls.lot_product = cls.env["product.product"].create(
            {
                "name": "Product Lot test",
                "type": "product",
                "tracking": "lot",
                "categ_id": cls.product_categ.id,
            }
        )
        cls.serial_product = cls.env["product.product"].create(
            {
                "name": "Product Serial test",
                "type": "product",
                "tracking": "serial",
                "categ_id": cls.product_categ.id,
            }
        )
        cls.serial1 = cls.env["stock.lot"].create(
            {
                "name": "T01",
                "product_id": cls.serial_product.id,
            }
        )

    def _make_lot_in_move(self, product, lot_vals, unit_cost=None):
        """
        Helper to create and validate a receipt move.
        lot_vals = [
            {'name': 'SN01', 'quantity': 1},
            {'name': 'SN02', 'quantity': 1},
        ]
        """
        unit_cost = unit_cost or product.standard_price
        quantity = sum([x["quantity"] for x in lot_vals])
        new_move = self.env["stock.move"].create(
            {
                "name": "in %s units @ %s per unit" % (str(quantity), str(unit_cost)),
                "product_id": product.id,
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.company_data[
                    "default_warehouse"
                ].lot_stock_id.id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": quantity,
                "price_unit": unit_cost,
                "picking_type_id": self.company_data["default_warehouse"].in_type_id.id,
            }
        )

        new_move._action_confirm()
        new_move._action_assign()

        i = 0
        for val in lot_vals:
            new_move.move_line_ids[i].lot_name = val["name"]
            new_move.move_line_ids[i].qty_done = val["quantity"]
            i += 1

        new_move._action_done()
        return new_move.with_context(svl=True)

    def _make_lot_out_move(self, product, lot_vals):
        """
        Helper to create and validate a delivery move.
        lot_vals = [
            {'lot': stock.lot(8,), 'quantity': 1},
            {'lot': stock.lot(9,), 'quantity': 1},
        ]
        """
        quantity = sum([x["quantity"] for x in lot_vals])
        new_move = self.env["stock.move"].create(
            {
                "name": "out %s units" % str(quantity),
                "product_id": product.id,
                "location_id": self.company_data["default_warehouse"].lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": quantity,
                "picking_type_id": self.company_data[
                    "default_warehouse"
                ].out_type_id.id,
            }
        )

        new_move._action_confirm()
        new_move._action_assign()

        i = 0
        for val in lot_vals:
            new_move.move_line_ids[i].lot_id = val["lot"]
            new_move.move_line_ids[i].qty_done = val["quantity"]
            i += 1

        new_move._action_done()
        return new_move.with_context(svl=True)

    # --------------------------------------------------------------------------
    # -- tests
    # --------------------------------------------------------------------------

    def test_specific_identification(self):
        """
        Verify that Specific Identification takes the value of SN02. FIFO would
        take the value of SN01 on an out move.
        """
        self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN01", "quantity": 1}],
            unit_cost=15000.0,
        )
        move2 = self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN02", "quantity": 1}],
            unit_cost=25000.0,
        )
        move_out = self._make_lot_out_move(
            self.serial_product,
            lot_vals=[{"lot": move2.move_line_ids.lot_id, "quantity": 1}],
        )

        in_value2 = move2.stock_valuation_layer_ids.unit_cost
        out_value = move_out.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            in_value2,
            out_value,
        )

    def test_extra_value(self):
        """
        Verify that Specific Identification gets cost from revaluations.
        """
        self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN03", "quantity": 1}],
            unit_cost=11000.0,
        )
        move2 = self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN04", "quantity": 1}],
            unit_cost=11000.0,
        )

        wiz = (
            self.env["stock.valuation.layer.lot.revaluation"]
            .sudo()
            .create(
                {
                    "company_id": self.company_data["company"].id,
                    "product_id": self.serial_product.id,
                    "lot_id": move2.move_line_ids.lot_id.id,
                    "added_value": -1000.0,
                    "account_id": self.company_data["default_account_stock_cost"].id,
                    "reason": "test serial revaluation",
                }
            )
        )
        wiz.action_validate_revaluation()

        move_out = self._make_lot_out_move(
            self.serial_product,
            lot_vals=[{"lot": move2.move_line_ids.lot_id, "quantity": 1}],
        )

        total_value = move2.stock_valuation_layer_ids.unit_cost - 1000
        out_value = move_out.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            total_value,
            out_value,
        )

    def test_return_value(self):
        """
        Verify that Specific Identification gets return cost from original out
        move.
        """
        move_in1 = self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN05", "quantity": 1}],
            unit_cost=11000.0,
        )
        move_in2 = self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN06", "quantity": 1}],
            unit_cost=12000.0,
        )
        move_in3 = self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN07", "quantity": 1}],
            unit_cost=13000.0,
        )

        self._make_lot_out_move(
            self.serial_product,
            lot_vals=[{"lot": move_in1.move_line_ids.lot_id, "quantity": 1}],
        )
        move_out2 = self._make_lot_out_move(
            self.serial_product,
            lot_vals=[{"lot": move_in2.move_line_ids.lot_id, "quantity": 1}],
        )
        self._make_lot_out_move(
            self.serial_product,
            lot_vals=[{"lot": move_in3.move_line_ids.lot_id, "quantity": 1}],
        )

        wiz = self.env["stock.return.picking"].create({})
        wiz.picking_id = move_out2.picking_id
        wiz._onchange_picking_id()
        wiz.product_return_moves.quantity = 1
        new_picking_id, pick_type_id = wiz._create_returns()
        new_pick = self.env["stock.picking"].browse(new_picking_id)

        new_pick.move_ids.move_line_ids.lot_id = move_out2.move_line_ids.lot_id
        new_pick.move_ids.move_line_ids.qty_done = 1
        new_pick._action_done()

        return_value = new_pick.move_ids.stock_valuation_layer_ids.unit_cost
        out_value = move_out2.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            return_value,
            out_value,
        )

    def test_lot_specific_identification(self):
        """
        Verify that Specific Identification takes the value of lot LT02. FIFO
        would take the value of LT01 on an out move.
        """
        self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT01", "quantity": 10}],
            unit_cost=15000.0,
        )
        move2 = self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT02", "quantity": 10}],
            unit_cost=25000.0,
        )
        move_out = self._make_lot_out_move(
            self.lot_product,
            lot_vals=[{"lot": move2.move_line_ids.lot_id, "quantity": 1}],
        )

        in_value2 = move2.stock_valuation_layer_ids.unit_cost
        out_value = move_out.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            in_value2,
            out_value,
        )

    def test_lot_extra_value(self):
        """
        Verify that Specific Identification gets cost from revaluations.
        """
        self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT03", "quantity": 10}],
            unit_cost=11000.0,
        )
        move2 = self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT04", "quantity": 10}],
            unit_cost=11000.0,
        )

        wiz = (
            self.env["stock.valuation.layer.lot.revaluation"]
            .with_context(default_product_id=self.lot_product.id)
            .sudo()
            .create(
                {
                    "company_id": self.company_data["company"].id,
                    # "product_id": self.lot_product.id,
                    "lot_id": move2.move_line_ids.lot_id.id,
                    "added_value": 1000.0,
                    "account_id": self.company_data["default_account_stock_cost"].id,
                    "reason": "test serial revaluation",
                }
            )
        )
        new_value = wiz.new_value
        wiz.action_validate_revaluation()

        move_out = self._make_lot_out_move(
            self.lot_product,
            lot_vals=[{"lot": move2.move_line_ids.lot_id, "quantity": 1}],
        )

        total_value = move2.stock_valuation_layer_ids.unit_cost + 100
        out_value = move_out.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            new_value,
            11000.0 * 10.0 + 1000.0,
        )
        self.assertEqual(
            total_value,
            out_value,
        )

    def test_lot_return_value(self):
        """
        Verify that Specific Identification gets return cost from original out
        move.
        """
        move_in1 = self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT05", "quantity": 10}],
            unit_cost=9000.0,
        )
        move_in2 = self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT06", "quantity": 10}],
            unit_cost=10000.0,
        )
        move_in3 = self._make_lot_in_move(
            self.lot_product,
            lot_vals=[{"name": "LT07", "quantity": 10}],
            unit_cost=11000.0,
        )

        self._make_lot_out_move(
            self.lot_product,
            lot_vals=[{"lot": move_in1.move_line_ids.lot_id, "quantity": 1}],
        )
        move_out2 = self._make_lot_out_move(
            self.lot_product,
            lot_vals=[{"lot": move_in2.move_line_ids.lot_id, "quantity": 1}],
        )
        self._make_lot_out_move(
            self.lot_product,
            lot_vals=[{"lot": move_in3.move_line_ids.lot_id, "quantity": 1}],
        )

        wiz = self.env["stock.return.picking"].create({})
        wiz.picking_id = move_out2.picking_id
        wiz._onchange_picking_id()
        wiz.product_return_moves.quantity = 1
        new_picking_id, pick_type_id = wiz._create_returns()
        new_pick = self.env["stock.picking"].browse(new_picking_id)

        new_pick.move_ids.move_line_ids.lot_id = move_out2.move_line_ids.lot_id
        new_pick.move_ids.move_line_ids.qty_done = 1
        new_pick._action_done()

        return_value = new_pick.move_ids.stock_valuation_layer_ids.unit_cost
        out_value = move_out2.stock_valuation_layer_ids.unit_cost

        self.assertEqual(
            return_value,
            out_value,
        )

    def test_disallow_negative_stock(self):
        """
        Verify that negative stock is not allowed.
        """
        new_move = self.env["stock.move"].create(
            {
                "name": "out 1 units",
                "product_id": self.serial_product.id,
                "location_id": self.company_data["default_warehouse"].lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "product_uom": self.env.ref("uom.product_uom_unit").id,
                "product_uom_qty": 1,
                "picking_type_id": self.company_data[
                    "default_warehouse"
                ].out_type_id.id,
                "move_line_ids": [
                    [
                        0,
                        0,
                        {
                            "product_id": self.serial_product.id,
                            "lot_id": self.serial1.id,
                            "qty_done": 1,
                        },
                    ]
                ],
            }
        )

        with self.assertRaises(ValidationError) as exc:
            new_move._action_done()
        self.assertEqual(
            exc.exception.args[0],
            "We can't process the move because the following lots/serials "
            "are not available: T01",
        )

    def test_revalue_sans_lot(self):
        """
        Verify that revaluation is not allowed without a lot/serial.
        """
        with self.assertRaises(UserError) as exc:
            self.serial_product.action_revaluation()
        self.assertEqual(
            exc.exception.args[0],
            "This product must be revalued by lot/serial",
        )

    def test_category_costing_conflict(self):
        """
        Verify that Specific Ident requires FIFO.
        """

        vals = {
            "name": "Test Categ 2",
            "property_cost_method": "average",
            "property_valuation": "real_time",
            "property_specific_ident_cost": True,
            "property_stock_valuation_account_id": self.company_data[
                "default_account_stock_valuation"
            ].id,
            "property_stock_account_input_categ_id": self.company_data[
                "default_account_stock_in"
            ].id,
            "property_stock_account_output_categ_id": self.company_data[
                "default_account_stock_out"
            ].id,
        }

        with self.assertRaises(ValidationError) as exc:
            self.env["product.category"].create(vals)
        self.assertEqual(
            exc.exception.args[0],
            "Costing by Lot/Serial requires FIFO as a "
            "fallback for untracked products",
        )

    def test_revalue_zero_stock_product(self):
        """
        Verify that revaluation requires positive product stock.
        """
        wiz_vals = {
            "company_id": self.company_data["company"].id,
            "lot_id": self.serial1.id,
            "added_value": 1000.0,
            "account_id": self.company_data["default_account_stock_cost"].id,
            "reason": "test serial revaluation",
        }
        with self.assertRaises(UserError) as exc:
            (
                self.env["stock.valuation.layer.lot.revaluation"]
                .with_context(default_product_id=self.lot_product.id)
                .sudo()
                .create(wiz_vals)
            )
        self.assertEqual(
            exc.exception.args[0],
            "You cannot revalue a product with an empty or negative stock.",
        )

    def test_revalue_zero_stock_lot(self):
        """
        Verify that revaluation requires positive lot stock.
        """
        self._make_lot_in_move(
            self.serial_product,
            lot_vals=[{"name": "SN01", "quantity": 1}],
            unit_cost=1500.0,
        )
        wiz_vals = {
            "company_id": self.company_data["company"].id,
            "added_value": 1000.0,
            "account_id": self.company_data["default_account_stock_cost"].id,
            "reason": "test serial revaluation",
        }
        with self.assertRaises(UserError) as exc:
            (
                self.env["stock.valuation.layer.lot.revaluation"]
                .with_context(
                    default_product_id=self.serial_product.id,
                    default_lot_id=self.serial1.id,
                )
                .sudo()
                .create(wiz_vals)
            )
        self.assertEqual(
            exc.exception.args[0],
            "You cannot revalue a lot with an empty or negative stock.",
        )
