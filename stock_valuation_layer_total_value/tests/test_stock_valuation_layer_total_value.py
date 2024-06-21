# Copyright 2022 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import tagged

from odoo.addons.stock_account.tests.test_anglo_saxon_valuation_reconciliation_common import (
    ValuationReconciliationTestCommon,
)


@tagged("-at_install", "post_install")
class TestValuationLayerTotalValue(ValuationReconciliationTestCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stock_account_product_categ = cls.env["product.category"].create(
            {
                "name": "Test category",
                "property_valuation": "real_time",
                "property_cost_method": "fifo",
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
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "product1",
                "type": "product",
                "categ_id": cls.stock_account_product_categ.id,
            }
        )

    def _make_in_move(self, product, quantity, unit_cost=None, create_picking=False):
        """Helper to create and validate a receipt move."""
        unit_cost = unit_cost or product.standard_price
        in_move = self.env["stock.move"].create(
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

        if create_picking:
            picking = self.env["stock.picking"].create(
                {
                    "picking_type_id": in_move.picking_type_id.id,
                    "location_id": in_move.location_id.id,
                    "location_dest_id": in_move.location_dest_id.id,
                }
            )
            in_move.write({"picking_id": picking.id})

        in_move._action_confirm()
        in_move._action_assign()
        in_move.move_line_ids.qty_done = quantity
        in_move._action_done()

        return in_move.with_context(svl=True)

    def test_valuation_layer_values(self):
        move1 = self._make_in_move(self.product1, 10, unit_cost=10, create_picking=True)
        move2 = self._make_in_move(self.product1, 5, unit_cost=15, create_picking=True)
        original_svl = move1.stock_valuation_layer_ids
        total_value_original = original_svl.total_value_with_additional_costs
        new_svl = move2.stock_valuation_layer_ids
        original_svl.write({"stock_valuation_layer_ids": [(4, new_svl.id)]})
        self.assertEqual(
            original_svl.total_value_with_additional_costs,
            total_value_original + new_svl.value,
        )
        self.assertEqual(
            original_svl.unit_price_with_extra_cost,
            original_svl.total_value_with_additional_costs / original_svl.quantity,
        )
