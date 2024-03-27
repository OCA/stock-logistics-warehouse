# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta

from odoo.tests import Form, tagged

from odoo.addons.mrp.tests.test_backorder import TestMrpProductionBackorder


@tagged("post_install", "-at_install")
class TestReservationMethodMrp(TestMrpProductionBackorder):
    """
    Test backported from V15
    """

    def test_reservation_method_w_mo(self):
        """Create a MO for 2 units, Produce 1 and create a backorder.
        The MO and the backorder should be assigned according to the reservation method
        defined in the default manufacturing operation type
        """

        def create_mo(date_planned_start=False):
            mo_form = Form(self.env["mrp.production"])
            mo_form.product_id = self.bom_1.product_id
            mo_form.bom_id = self.bom_1
            mo_form.product_qty = 2
            if date_planned_start:
                mo_form.date_planned_start = date_planned_start
            mo = mo_form.save()
            mo.action_confirm()
            return mo

        def produce_one(mo):
            mo_form = Form(mo)
            mo_form.qty_producing = 1
            mo = mo_form.save()
            action = mo.button_mark_done()
            backorder = Form(
                self.env["mrp.production.backorder"].with_context(**action["context"])
            )
            backorder.save().action_backorder()
            return mo.procurement_group_id.mrp_production_ids[-1]

        # Make some stock and reserve
        for product in self.bom_1.bom_line_ids.product_id:
            product.type = "product"
            self.env["stock.quant"].with_context(inventory_mode=True).create(
                {
                    "product_id": product.id,
                    "inventory_quantity": 100,
                    "location_id": self.stock_location.id,
                }
            )

        default_picking_type_id = self.env["mrp.production"]._get_default_picking_type()
        default_picking_type = self.env["stock.picking.type"].browse(
            default_picking_type_id
        )

        # make sure generated MO will auto-assign
        default_picking_type.reservation_method = "at_confirm"
        production = create_mo()
        self.assertEqual(production.state, "confirmed")
        self.assertEqual(production.reserve_visible, False)
        # check whether the backorder follows the same scenario as the original MO
        backorder = produce_one(production)
        self.assertEqual(backorder.state, "confirmed")
        self.assertEqual(backorder.reserve_visible, False)

        # make sure generated MO will does not auto-assign
        default_picking_type.reservation_method = "manual"
        production = create_mo()
        self.assertEqual(production.state, "confirmed")
        self.assertEqual(production.reserve_visible, True)
        backorder = produce_one(production)
        self.assertEqual(backorder.state, "confirmed")
        self.assertEqual(backorder.reserve_visible, True)

        # make sure generated MO auto-assigns according to scheduled date
        default_picking_type.reservation_method = "by_date"
        default_picking_type.reservation_days_before = 2
        # too early for scheduled date => don't auto-assign
        production = create_mo(datetime.now() + timedelta(days=10))
        self.assertEqual(production.state, "confirmed")
        self.assertEqual(production.reserve_visible, True)
        backorder = produce_one(production)
        self.assertEqual(backorder.state, "confirmed")
        self.assertEqual(backorder.reserve_visible, True)

        # within scheduled date + reservation days before => auto-assign
        production = create_mo()
        self.assertEqual(production.state, "confirmed")
        self.assertEqual(production.reserve_visible, False)
        backorder = produce_one(production)
        self.assertEqual(backorder.state, "confirmed")
        self.assertEqual(backorder.reserve_visible, False)
