from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class InventoryAdjustmentsGroup(models.Model):
    _name = "stock.inventory"
    _description = "Inventory Adjustment Group"
    _order = "date desc, id desc"
    _inherit = [
        "mail.thread",
    ]

    name = fields.Char(
        required=True,
        default="Inventory",
        string="Inventory Reference",
        states={"draft": [("readonly", False)]},
        readonly=True,
    )

    date = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        states={"draft": [("readonly", False)]},
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        readonly=True,
        index=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection(
        [("draft", "Draft"), ("in_progress", "In Progress"), ("done", "Done")],
        default="draft",
        tracking=True,
    )

    owner_id = fields.Many2one(
        "res.partner", "Owner", help="This is the owner of the inventory adjustment"
    )

    location_ids = fields.Many2many(
        "stock.location",
        string="Locations",
        domain="[('usage', '=', 'internal'), "
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
    )

    product_selection = fields.Selection(
        [
            ("all", "All Products"),
            ("manual", "Manual Selection"),
            ("category", "Product Category"),
            ("one", "One Product"),
            ("lot", "Lot/Serial Number"),
        ],
        default="all",
        required=True,
    )

    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
    )

    stock_quant_ids = fields.Many2many(
        "stock.quant",
        string="Inventory Adjustment",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
    )

    category_id = fields.Many2one("product.category", string="Product Category")

    lot_ids = fields.Many2many(
        "stock.lot",
        string="Lot/Serial Numbers",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
    )

    stock_move_ids = fields.One2many(
        "stock.move.line",
        "inventory_adjustment_id",
        string="Inventory Adjustments Done",
    )

    count_stock_quants = fields.Integer(
        compute="_compute_count_stock_quants", string="# Adjustments"
    )

    count_stock_quants_string = fields.Char(
        compute="_compute_count_stock_quants", string="Adjustments"
    )

    count_stock_moves = fields.Integer(
        compute="_compute_count_stock_moves", string="Stock Moves Lines"
    )

    exclude_sublocation = fields.Boolean(
        help="If enabled, it will only take into account "
        "the locations selected, and not their children."
    )

    responsible_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned to",
        states={"draft": [("readonly", False)]},
        readonly=True,
        help="Specific responsible of Inventory Adjustment.",
    )

    @api.depends("stock_quant_ids")
    def _compute_count_stock_quants(self):
        self.count_stock_quants = len(self.stock_quant_ids)
        count_todo = len(self.stock_quant_ids.filtered(lambda sq: sq.to_do))
        self.count_stock_quants_string = "{} / {}".format(
            count_todo, self.count_stock_quants
        )

    @api.depends("stock_move_ids")
    def _compute_count_stock_moves(self):
        sm_ids = self.mapped("stock_move_ids").ids
        self.count_stock_moves = len(sm_ids)

    def _get_quants(self, locations):
        domain = []
        base_domain = self._get_base_domain(locations)
        if self.product_selection == "all":
            domain = self._get_domain_all_quants(base_domain)
        elif self.product_selection == "manual":
            domain = self._get_domain_manual_quants(base_domain)
        elif self.product_selection == "one":
            domain = self._get_domain_one_quant(base_domain)
        elif self.product_selection == "lot":
            domain = self._get_domain_lot_quants(base_domain)
        elif self.product_selection == "category":
            domain = self._get_domain_category_quants(base_domain)
        return self.env["stock.quant"].search(domain)

    def _get_base_domain(self, locations):
        return (
            [
                ("location_id", "in", locations.mapped("id")),
            ]
            if self.exclude_sublocation
            else [
                ("location_id", "child_of", locations.child_internal_location_ids.ids),
            ]
        )

    def _get_domain_all_quants(self, base_domain):
        return base_domain

    def _get_domain_manual_quants(self, base_domain):
        return expression.AND(
            [base_domain, [("product_id", "in", self.product_ids.ids)]]
        )

    def _get_domain_one_quant(self, base_domain):
        return expression.AND(
            [
                base_domain,
                [
                    ("product_id", "in", self.product_ids.ids),
                ],
            ]
        )

    def _get_domain_lot_quants(self, base_domain):
        return expression.AND(
            [
                base_domain,
                [
                    ("product_id", "in", self.product_ids.ids),
                    ("lot_id", "in", self.lot_ids.ids),
                ],
            ]
        )

    def _get_domain_category_quants(self, base_domain):
        return expression.AND(
            [
                base_domain,
                [
                    "|",
                    ("product_id.categ_id", "=", self.category_id.id),
                    ("product_id.categ_id", "in", self.category_id.child_id.ids),
                ],
            ]
        )

    def refresh_stock_quant_ids(self):
        for rec in self:
            rec.stock_quant_ids = rec._get_quants(rec.location_ids)

    def action_state_to_in_progress(self):
        active_rec = self.env["stock.inventory"].search(
            [
                ("state", "=", "in_progress"),
                ("location_ids", "child_of", self.location_ids.ids),
            ],
            limit=1,
        )
        if active_rec:
            raise ValidationError(
                _(
                    "There's already an Adjustment in Process using one requested Location: %s"
                )
                % active_rec.name
            )
        self.state = "in_progress"
        self.refresh_stock_quant_ids()
        self.stock_quant_ids.update(
            {
                "to_do": True,
                "user_id": self.responsible_id,
                "inventory_date": self.date,
            }
        )
        return

    def action_state_to_done(self):
        self.state = "done"
        self.stock_quant_ids.update(
            {
                "to_do": True,
                "user_id": False,
                "inventory_date": False,
            }
        )
        return

    def action_auto_state_to_done(self):
        self.ensure_one()
        if not any(self.stock_quant_ids.filtered(lambda sq: sq.to_do)):
            self.action_state_to_done()
        return

    def action_state_to_draft(self):
        self.state = "draft"
        self.stock_quant_ids.update(
            {
                "to_do": True,
                "user_id": False,
                "inventory_date": False,
            }
        )
        self.stock_quant_ids = None
        return

    def action_view_inventory_adjustment(self):
        result = self.env["stock.quant"].action_view_inventory()
        result["domain"] = [("id", "in", self.stock_quant_ids.ids)]
        result["search_view_id"] = self.env.ref("stock.quant_search_view").id
        result["context"]["search_default_to_do"] = 1
        return result

    def action_view_stock_moves(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_inventory.action_view_stock_move_line_inventory_tree"
        )
        sm_ids = self.mapped("stock_move_ids").ids
        result["domain"] = [("id", "in", sm_ids)]
        result["context"] = []
        return result

    @api.constrains("state", "location_ids")
    def _check_inventory_in_progress_not_override(self):
        inventories = self.search([("state", "=", "in_progress")])
        for rec in inventories:
            inventory = inventories.filtered(
                lambda x: x.id != rec.id
                and (
                    any(i in x.location_ids for i in rec.location_ids)
                    or (
                        any(
                            i in x.location_ids.child_internal_location_ids
                            for i in rec.location_ids
                        )
                        and not x.exclude_sublocation
                    )
                )
            )
            if len(inventory) > 0:
                raise ValidationError(
                    _(
                        "Cannot be more than one in progress inventory adjustment "
                        "affecting the same location at the same time."
                    )
                )

    @api.constrains("product_selection", "product_ids")
    def _check_one_product_in_product_selection(self):
        for rec in self:
            if len(rec.product_ids) > 1:
                if rec.product_selection == "one":
                    raise ValidationError(
                        _(
                            "When 'Product Selection: One Product' is selected"
                            " you are only able to add one product."
                        )
                    )
                elif rec.product_selection == "lot":
                    raise ValidationError(
                        _(
                            "When 'Product Selection: Lot Serial Number' is selected"
                            " you are only able to add one product."
                        )
                    )
