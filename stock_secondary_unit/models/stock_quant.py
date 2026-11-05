# Copyright 2025 Quartile (https://wwww.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.float_utils import float_round


class StockQuant(models.Model):
    _inherit = ["stock.quant", "product.secondary.unit.mixin"]
    _name = "stock.quant"
    _secondary_unit_fields = {"qty_field": "quantity", "uom_field": "product_uom_id"}
    # Secondary unit inputs and the quantity field each of them drives
    _secondary_uom_inventory_fields = {
        "secondary_uom_inventory_quantity": "inventory_quantity",
        "secondary_uom_inventory_quantity_auto_apply": "inventory_quantity_auto_apply",
    }

    secondary_uom_id = fields.Many2one(
        related="product_id.stock_secondary_uom_id",
        store=True,
        default=None,
    )
    # Need precompute=False since secondary_uom_id is not precompute field and we
    # shouldn't depend for compute method of precompute field.
    secondary_uom_qty = fields.Float(precompute=False)
    secondary_uom_inventory_quantity = fields.Float(
        string="Counted Quantity (Secondary Unit)",
        digits="Product Unit of Measure",
        compute="_compute_secondary_uom_inventory_quantity",
        readonly=False,
        help="The product's counted quantity, expressed in the secondary unit. "
        "Filling it in sets the counted quantity accordingly.",
    )
    secondary_uom_inventory_quantity_auto_apply = fields.Float(
        string="On Hand Quantity (Secondary Unit)",
        digits="Product Unit of Measure",
        compute="_compute_secondary_uom_inventory_quantity_auto_apply",
        readonly=False,
        groups="stock.group_stock_user",
        help="The product's on hand quantity, expressed in the secondary unit. "
        "Filling it in applies the quantity right away.",
    )
    secondary_uom_dependency_type = fields.Selection(
        related="secondary_uom_id.dependency_type"
    )

    @api.model
    def _get_secondary_uom_qty_depends(self):
        # The quant shows the current on hand quantity, so it follows changes of
        # the unit itself too
        return super()._get_secondary_uom_qty_depends() + [
            "secondary_uom_id",
            "secondary_uom_id.factor",
            "secondary_uom_id.dependency_type",
        ]

    def _compute_secondary_uom_qty(self):
        # A quant has no counted secondary quantity of its own, so a
        # secondary_priority unit is converted from the on hand quantity, as the
        # inventory quantity fields already do
        priority_quants = self.filtered(
            lambda q: q.secondary_uom_id.dependency_type == "secondary_priority"
        )
        res = super(StockQuant, self - priority_quants)._compute_secondary_uom_qty()
        for quant in priority_quants:
            quant.secondary_uom_qty = quant._convert_qty_to_secondary_uom(
                quant.quantity
            )
        return res

    @api.model
    def _merge_quants(self):
        # Core merges duplicated quants in SQL, so recompute the secondary
        # quantity of the surviving ones
        query = "SELECT min(id) FROM stock_quant"
        params = []
        if self._ids:
            query += " WHERE location_id IN %s AND product_id IN %s"
            params = [tuple(self.location_id.ids), tuple(self.product_id.ids)]
        query += """
            GROUP BY product_id, company_id, location_id, lot_id, package_id, owner_id
            HAVING count(id) > 1
        """
        self.env["stock.quant"].flush_model()
        self.env.cr.execute(query, params)
        survivor_ids = [row[0] for row in self.env.cr.fetchall()]
        res = super()._merge_quants()
        if survivor_ids:
            survivors = self.browse(survivor_ids).exists()
            survivors.modified(["quantity"])
            survivors.flush_recordset(["secondary_uom_qty"])
        return res

    @api.depends("inventory_quantity", "secondary_uom_id")
    def _compute_secondary_uom_inventory_quantity(self):
        for quant in self:
            quant.secondary_uom_inventory_quantity = (
                quant._get_secondary_uom_inventory_qty(quant.inventory_quantity)
            )

    @api.depends("quantity", "secondary_uom_id")
    def _compute_secondary_uom_inventory_quantity_auto_apply(self):
        for quant in self:
            quant.secondary_uom_inventory_quantity_auto_apply = (
                quant._get_secondary_uom_inventory_qty(quant.quantity)
            )

    def _get_secondary_uom_inventory_qty(self, qty):
        self.ensure_one()
        if not self._is_convertible_secondary_uom(self.secondary_uom_id):
            return 0.0
        return self._convert_qty_to_secondary_uom(qty)

    @api.onchange("secondary_uom_inventory_quantity")
    def _onchange_secondary_uom_inventory_quantity(self):
        self._set_quantity_from_secondary(
            "inventory_quantity", self.secondary_uom_inventory_quantity
        )

    @api.onchange("secondary_uom_inventory_quantity_auto_apply")
    def _onchange_secondary_uom_inventory_quantity_auto_apply(self):
        self._set_quantity_from_secondary(
            "inventory_quantity_auto_apply",
            self.secondary_uom_inventory_quantity_auto_apply,
        )

    def _onchange_secondary_uom_id_for_qty(self):
        # A quant's quantity is never driven by its secondary quantity; the
        # mixin's onchange would round the on hand quantity to the secondary unit
        return

    def _set_quantity_from_secondary(self, qty_field, secondary_uom_qty):
        for quant in self:
            if not quant._is_convertible_secondary_uom(quant.secondary_uom_id):
                continue
            quant[qty_field] = self._convert_secondary_uom_qty_to_qty(
                quant.secondary_uom_id, secondary_uom_qty, quant.product_uom_id
            )

    @api.model
    def _is_driven_by_secondary_uom(self, vals, secondary_field):
        qty_field = self._secondary_uom_inventory_fields[secondary_field]
        return qty_field not in vals and secondary_field in vals

    @api.model_create_multi
    def create(self, vals_list):
        inventory_fields = self._secondary_uom_inventory_fields
        for vals in vals_list:
            for secondary_field, qty_field in inventory_fields.items():
                driven = self._is_driven_by_secondary_uom(vals, secondary_field)
                secondary_uom_qty = vals.pop(secondary_field, 0.0)
                if not driven:
                    continue
                product = self.env["product.product"].browse(vals.get("product_id"))
                secondary_uom = product.stock_secondary_uom_id
                if not self._is_convertible_secondary_uom(secondary_uom):
                    continue
                vals[qty_field] = self._convert_secondary_uom_qty_to_qty(
                    secondary_uom, secondary_uom_qty, product.uom_id
                )
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        for secondary_field, qty_field in self._secondary_uom_inventory_fields.items():
            if self._is_driven_by_secondary_uom(vals, secondary_field):
                self._set_quantity_from_secondary(qty_field, vals[secondary_field])
        return res

    @api.model
    def _get_inventory_fields_write(self):
        return super()._get_inventory_fields_write() + list(
            self._secondary_uom_inventory_fields
        )

    @api.model
    def _is_convertible_secondary_uom(self, secondary_uom):
        return bool(secondary_uom) and secondary_uom.dependency_type != "independent"

    @api.model
    def _convert_secondary_uom_qty_to_qty(self, secondary_uom, secondary_uom_qty, uom):
        return float_round(
            secondary_uom_qty * secondary_uom.factor, precision_rounding=uom.rounding
        )
