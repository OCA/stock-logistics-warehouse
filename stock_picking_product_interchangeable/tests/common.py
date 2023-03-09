from odoo.tests import TransactionCase


class StockPickingProductInterchangeableCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(StockPickingProductInterchangeableCommon, cls).setUpClass()
        cls.product_fork = cls.env.ref(
            "stock_picking_product_interchangeable.product_product_fork"
        )
        cls.product_spoon = cls.env.ref(
            "stock_picking_product_interchangeable.product_product_spoon"
        )
        cls.product_knife = cls.env.ref(
            "stock_picking_product_interchangeable.product_product_knife"
        )
        cls.product_chopsticks = cls.env.ref(
            "stock_picking_product_interchangeable.product_product_chopsticks"
        )
        cls.product_tmpl_napkin = cls.env.ref(
            "stock_picking_product_interchangeable.product_template_napkin"
        )
        cls.product_tmpl_plate = cls.env.ref(
            "stock_picking_product_interchangeable.product_template_plate"
        )
        cls.product_napkin = cls.product_tmpl_napkin.product_variant_id
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.res_partner_bob = cls.env.ref(
            "stock_picking_product_interchangeable.res_partner_bob"
        )
