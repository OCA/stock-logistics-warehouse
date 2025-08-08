import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockResupplyOrder(models.Model):
    _name = "stock.resupply.order"
    _inherit = ["mail.thread"]
    _description = """
    Creates resupply orders that create procurements
    following stocks that are already in the destination location
    """

    location_id = fields.Many2one(
        "stock.location",
        required=True,
        help="The stock location that needs to be restocked",
    )

    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )

    stock_resupply_order_lines = fields.One2many(
        "stock.resupply.order.line",
        inverse_name="stock_resupply_order_id",
        help="All product quantities desired at the given location",
        string="Desired products quantities",
    )

    procurement_group_id = fields.Many2one(
        "procurement.group", string="Generated procurement"
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
        ],
        "Status",
        help=(
            "Resupply order state: \n"
            "* draft: The order has not been confirmed yet.\n"
            "* done: The procurements have been created. \n"
        ),
        copy=False,
        readonly=True,
        tracking=True,
        store=True,
        default="draft",
    )

    picking_ids = fields.One2many(
        "stock.picking",
        compute="_compute_picking_ids",
        string="Generated stock pickings",
        readonly=True,
    )

    picking_count = fields.Integer(
        string="Picking count", compute="_compute_picking_ids", readonly=True
    )

    @api.depends("procurement_group_id.stock_move_ids.picking_id")
    def _compute_picking_ids(self):
        for record in self:
            record.picking_ids = record.procurement_group_id.stock_move_ids.picking_id
            record.picking_count = len(record.picking_ids)

    def action_run(self):
        if self.procurement_group_id:
            return self.procurement_group_id

        self.procurement_group_id = self.env["procurement.group"].create(
            self._get_procurement_group_parameters()
        )

        quant_groups = self._get_existing_quants()

        procurements = []

        for line in self.stock_resupply_order_lines:
            # service products have no tracking/lot and cannot be run in procurement
            if line.product_id.product_tmpl_id.type == "service":
                continue

            available_quantity = self._get_available_quantity_for_product(
                quant_groups, line
            )

            if available_quantity < line.quantity:
                procurements.append(
                    self.env["procurement.group"].Procurement(
                        product_id=line.product_id,
                        product_qty=line.quantity - available_quantity,
                        product_uom=line.product_id.product_tmpl_id.uom_id,
                        location_id=self.location_id,
                        name=f"Resupply Order to {self.location_id.name}",
                        origin=f"Resupply Order to {self.location_id.name}",
                        company_id=self.company_id,
                        values=self._get_procurement_values(),
                    )
                )

        if procurements:
            self.env["procurement.group"].run(procurements)

        self.state = "done"

        return self.procurement_group_id

    @api.model
    def _get_available_quantity_for_product(
        self, quant_groups, stock_resupply_order_line
    ):
        try:
            # I could not find a way to merge stock_resupply_order_lines
            # with the quant_groups query, so it is retrieved with a product
            # id search here. Not ideal, but it works.
            group = next(
                group
                for group in quant_groups
                if group["product_id"][0] == stock_resupply_order_line.product_id.id
            )

            return group["quantity"] - group["reserved_quantity"]
        except StopIteration:
            return 0

    def _get_procurement_group_parameters(self):
        """
        Values to pass to the procurement group constructor.
        """

        self.ensure_one()

        return {
            "name": (f"Resupply Order {self.location_id.name}"),
            "move_type": "one",
        }

    def _get_procurement_values(self):
        """
        Values to pass to the procurement once the order is run.
        """

        self.ensure_one()

        return {
            "group_id": self.procurement_group_id,
        }

    def _get_existing_quants(self):
        """
        Get stock quants at the targeted location. Override if you need to
        apply specific constraints.
        """

        self.ensure_one()

        return (
            self.env["stock.quant"]
            .sudo()
            .read_group(
                domain=[
                    ("location_id", "=", self.location_id.id),
                    (
                        "product_id",
                        "in",
                        self.stock_resupply_order_lines.product_id.ids,
                    ),
                ],
                # Cant aggregate available_quantity here.
                fields=["product_id", "quantity:sum", "reserved_quantity:sum"],
                groupby=["product_id"],
                orderby="product_id",
                lazy=False,
            )
        )

    def action_view_transfers(self):
        pickings = self.procurement_group_id.stock_move_ids.picking_id

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_picking_tree_all"
        )

        pickings = self.procurement_group_id.stock_move_ids.picking_id
        if len(pickings) > 1:
            action["domain"] = [("id", "in", pickings.ids)]
        elif pickings:
            action["views"] = [(self.env.ref("stock.view_picking_form").id, "form")]
            action["res_id"] = pickings.id
        return action
