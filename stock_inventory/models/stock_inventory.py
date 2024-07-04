from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
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
        readonly=True,
    )

    date = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        readonly=True,
        index=True,
        default=lambda self: self.env.company,
        required=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )

    owner_id = fields.Many2one(
        "res.partner",
        "Owner",
        help="This is the owner of the inventory adjustment",
        readonly=True,
    )

    location_ids = fields.Many2many(
        "stock.location",
        string="Locations",
        domain="[('usage', '=', 'internal'), "
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
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
        readonly=True,
    )

    product_ids = fields.Many2many(
        "product.product",
        string="Products",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
    )

    stock_quant_ids = fields.Many2many(
        "stock.quant",
        string="Inventory Adjustment",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
    )

    category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        readonly=True,
    )

    lot_ids = fields.Many2many(
        "stock.lot",
        string="Lot/Serial Numbers",
        domain="['|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
    )

    stock_move_ids = fields.One2many(
        "stock.move.line",
        "inventory_adjustment_id",
        string="Inventory Adjustments Done",
        readonly=True,
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
    action_state_to_cancel_allowed = fields.Boolean(
        compute="_compute_action_state_to_cancel_allowed"
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
        for rec in self:
            quants = rec.stock_quant_ids
            quants_to_do = quants.filtered(lambda q: q.to_do)
            count_todo = len(quants_to_do)
            rec.count_stock_quants = len(quants)
            rec.count_stock_quants_string = f"{count_todo} / {rec.count_stock_quants}"

    @api.depends("stock_move_ids")
    def _compute_count_stock_moves(self):
        group_fname = "inventory_adjustment_id"
        group_data = self.env["stock.move.line"].read_group(
            [
                (group_fname, "in", self.ids),
            ],
            [group_fname],
            [group_fname],
        )
        data_by_adj_id = {
            row[group_fname][0]: row.get(f"{group_fname}_count", 0)
            for row in group_data
        }
        for rec in self:
            rec.count_stock_moves = data_by_adj_id.get(rec.id, 0)

    def _compute_action_state_to_cancel_allowed(self):
        for rec in self:
            rec.action_state_to_cancel_allowed = rec.state == "draft"

    def _get_quants(self, locations):
        self.ensure_one()
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
        self.ensure_one()
        return expression.AND(
            [base_domain, [("product_id", "in", self.product_ids.ids)]]
        )

    def _get_domain_one_quant(self, base_domain):
        self.ensure_one()
        return expression.AND(
            [
                base_domain,
                [
                    ("product_id", "in", self.product_ids.ids),
                ],
            ]
        )

    def _get_domain_lot_quants(self, base_domain):
        self.ensure_one()
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
        self.ensure_one()
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

    def _get_quant_joined_names(self, quants, field):
        return ", ".join(quants.mapped(f"{field}.display_name"))

    def action_state_to_in_progress(self):
        self.ensure_one()
        search_filter = [
            (
                "location_id",
                "child_of" if not self.exclude_sublocation else "in",
                self.location_ids.ids,
            ),
            ("to_do", "=", True),
        ]

        if self.product_ids:
            search_filter.append(("product_id", "in", self.product_ids.ids))
            error_field = "product_id"
            error_message = _(
                "There are active adjustments for the requested products: %s"
            )
        else:
            error_field = "location_id"
            error_message = _(
                "There's already an Adjustment in Process using one "
                "requested Location: %s"
            )

        quants = self.env["stock.quant"].search(search_filter)
        if quants:
            names = self._get_quant_joined_names(quants, error_field)
            raise ValidationError(error_message % names)

        quants = self._get_quants(self.location_ids)
        self.write(
            {
                "state": "in_progress",
                "stock_quant_ids": [(6, 0, quants.ids)],
            }
        )
        quants.write(
            {
                "to_do": True,
                "user_id": self.responsible_id,
                "inventory_date": self.date,
            }
        )
        return

    def action_state_to_done(self):
        self.ensure_one()
        self.state = "done"
        self.stock_quant_ids.update(
            {
                "to_do": False,
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
        self.ensure_one()
        self.state = "draft"
        self.stock_quant_ids.update(
            {
                "to_do": False,
                "user_id": False,
                "inventory_date": False,
            }
        )
        self.stock_quant_ids = None
        return

    def action_state_to_cancel(self):
        self.ensure_one()
        self._check_action_state_to_cancel()
        self.write(
            {
                "state": "cancel",
            }
        )

    def _check_action_state_to_cancel(self):
        for rec in self:
            if not rec.action_state_to_cancel_allowed:
                raise UserError(
                    _(
                        "You can't cancel this inventory %(display_name)s.",
                        display_name=rec.display_name,
                    )
                )

    def action_view_inventory_adjustment(self):
        self.ensure_one()
        result = self.env["stock.quant"].action_view_inventory()
        context = result.get("context", {})
        context.update(
            {
                "search_default_to_do": 1,
                "inventory_id": self.id,
                "default_to_do": True,
            }
        )
        result.update(
            {
                "domain": [("id", "in", self.stock_quant_ids.ids)],
                "search_view_id": self.env.ref("stock.quant_search_view").id,
                "context": context,
            }
        )
        return result

    def action_view_stock_moves(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_inventory.action_view_stock_move_line_inventory_tree"
        )
        result["domain"] = [("inventory_adjustment_id", "=", self.id)]
        result["context"] = {}
        return result

    def _check_inventory_in_progress_not_override(self):
        for rec in self:
            if rec.state == "in_progress":
                location_condition = [
                    (
                        "location_ids",
                        "child_of" if not rec.exclude_sublocation else "in",
                        rec.location_ids.ids,
                    )
                ]
                if rec.product_ids:
                    product_condition = [
                        ("state", "=", "in_progress"),
                        ("id", "!=", rec.id),
                        ("product_ids", "in", rec.product_ids.ids),
                    ] + location_condition
                    inventories = self.search(product_condition)
                else:
                    inventories = self.search(
                        [("state", "=", "in_progress"), ("id", "!=", rec.id)]
                        + location_condition
                    )
                for inventory in inventories:
                    if any(
                        i in inventory.location_ids.ids for i in rec.location_ids.ids
                    ):
                        raise ValidationError(
                            _(
                                "Cannot have more than one in-progress inventory "
                                "adjustment affecting the same location or product "
                                "at the same time."
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
