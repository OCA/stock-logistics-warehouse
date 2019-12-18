# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase


class TestProductSecondaryUnit(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        ProductAttribute = cls.env["product.attribute"]
        ProductAttributeValue = cls.env["product.attribute.value"]
        cls.attribute_color = ProductAttribute.create({"name": "test_color"})
        cls.attribute_value_white = ProductAttributeValue.create(
            {"name": "test_white", "attribute_id": cls.attribute_color.id}
        )
        cls.attribute_value_black = ProductAttributeValue.create(
            {"name": "test_black", "attribute_id": cls.attribute_color.id}
        )
        cls.product_template = cls.env["product.template"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "type": "product",
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "code": "A",
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.5,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "code": "B",
                            "name": "unit-900",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.9,
                        },
                    ),
                ],
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attribute_color.id,
                            "value_ids": [
                                (4, cls.attribute_value_white.id),
                                (4, cls.attribute_value_black.id),
                            ],
                        },
                    )
                ],
            }
        )
        secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product_template.id)], limit=1
        )
        cls.product_template.write({"stock_secondary_uom_id": secondary_unit.id})
        StockQuant = cls.env["stock.quant"]
        cls.quant_white = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[0].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )
        cls.quant_black = StockQuant.create(
            {
                "product_id": cls.product_template.product_variant_ids[1].id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "quantity": 10.0,
            }
        )

    def test_01_stock_secondary_unit_template(self):
        self.assertEqual(self.product_template.secondary_unit_qty_available, 40.0)

    def test_02_stock_secondary_unit_variant(self):
        for variant in self.product_template.product_variant_ids.filtered(
            "product_template_attribute_value_ids"
        ):
            self.assertEqual(variant.secondary_unit_qty_available, 20)

    def test_03_stock_picking_secondary_unit(self):
        StockPicking = self.env["stock.picking"]
        product1 = self.product_template.product_variant_ids[0]
        location = self.env.ref("stock.stock_location_suppliers")
        location_dest = self.env.ref("stock.stock_location_stock")
        picking_type = self.env.ref("stock.picking_type_in")
        move_vals = {
            "product_id": product1.id,
            "name": product1.display_name,
            "secondary_uom_id": product1.secondary_uom_ids[0].id,
            "product_uom": product1.uom_id.id,
            "product_uom_qty": 10.0,
            "location_id": location.id,
            "location_dest_id": location_dest.id,
        }
        do_vals = {
            "location_id": location.id,
            "location_dest_id": location_dest.id,
            "picking_type_id": picking_type.id,
            "move_ids_without_package": [
                (0, None, move_vals),
                (0, None, move_vals),
            ],  # 2 moves
        }
        delivery_order = StockPicking.create(do_vals)
        delivery_order.action_confirm()
        # Move is merged into 1 line for both stock.move and stock.move.line
        self.assertEquals(len(delivery_order.move_lines), 1)
        self.assertEquals(len(delivery_order.move_line_ids), 1)
        # Qty merged to 20, and secondary unit qty is 40line
        uom_qty = sum(delivery_order.move_lines.mapped("product_uom_qty"))
        secondary_uom_qty = sum(
            delivery_order.move_line_ids.mapped("secondary_uom_qty")
        )
        self.assertEquals(uom_qty, 20.0)
        self.assertEquals(secondary_uom_qty, 40.0)
