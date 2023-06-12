import base64
import csv
from io import StringIO

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockImport(models.TransientModel):
    _name = "stock.import"
    _description = "Update Stock Quantities from CSV File"

    file_name = fields.Char()
    file_import = fields.Binary(string="CSV File", required=True)

    def _default_location_id(self):
        default_wh = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        return default_wh.lot_stock_id

    location_id = fields.Many2one(
        "stock.location",
        default=_default_location_id,
        required=True,
        domain="[('usage', '=', 'internal')]",
        help="Update stock in this location",
    )

    internal_ref_col_id = fields.Many2one(
        "stock.import.header",
        string="Internal Reference Column",
        domain="[('stock_import_id', '=', id)]",
    )
    quantity_col_id = fields.Many2one(
        "stock.import.header",
        string="Quantity Column",
        domain="[('stock_import_id', '=', id)]",
    )

    import_headers = fields.One2many(
        "stock.import.header",
        "stock_import_id",
    )
    error_message = fields.Text(readonly=True)

    state = fields.Selection(
        [("choose", "choose"), ("import", "import"), ("error", "error")],
        default="choose",
    )
    strict_mode = fields.Boolean(
        help="""
        If enabled, it will complete the import of the stocks
        only if the file contains only valid product codes.
        """,
        default=False,
    )

    def button_load_csv_data(self):
        self.ensure_one()
        csv_data = base64.b64decode(self.file_import)
        data_file = StringIO(csv_data.decode("utf-8"))

        reader = csv.reader(data_file)
        headers = next(reader)

        def_code_index = (
            headers.index(self.internal_ref_col_id.name)
            if self.internal_ref_col_id.name in headers
            else 0
        )
        quantity_index = (
            headers.index(self.quantity_col_id.name)
            if self.quantity_col_id.name in headers
            else 1
        )
        Quant = self.env["stock.quant"]

        errors, values = self.validate_data(reader, def_code_index, quantity_index)

        if errors:
            self.error_message = (
                (
                    _("Stock not updated for the following products")
                    if not self.strict_mode
                    else _("Stock not updated for any product")
                )
                + "\n\n - "
                + "\n - ".join(errors)
            )
            self.state = "error"

            if self.strict_mode:
                raise UserError(self.error_message)

        # Data import
        quant_ids = self.env["stock.quant"]
        for product_id, product_qty in values.items():
            quant = Quant.search(
                [
                    ("product_id.id", "=", product_id),
                    ("location_id", "=", self.location_id.id),
                ],
                limit=1,
            )
            if quant:
                quant.inventory_quantity = product_qty
            else:
                quant = Quant.create(
                    {
                        "product_id": product_id,
                        "inventory_quantity": product_qty,
                        "location_id": self.location_id.id,
                    }
                )
            quant_ids += quant

        quant_ids.action_apply_inventory()

        if errors:
            return {
                "name": _("Import stock quantities"),
                "type": "ir.actions.act_window",
                "res_model": "stock.import",
                "view_mode": "form",
                "res_id": self.id,
                "views": [(False, "form")],
                "target": "new",
            }

        return self.action_reload()

    def button_analyze_csv(self):
        self.ensure_one()

        self.import_headers = [fields.Command.clear()]
        csv_data = base64.b64decode(self.file_import)
        data_file = StringIO(csv_data.decode("utf-8"))
        reader = csv.reader(data_file)
        headers = next(reader)

        if len(headers) < 2:
            raise UserError(_("CSV file must have at least two columns"))

        for i, item in enumerate(headers):
            record = self.env["stock.import.header"].create(
                {
                    "name": item,
                    "stock_import_id": self.id,
                }
            )
            if i == 0:
                self.internal_ref_col_id = record
            elif i == 1:
                self.quantity_col_id = record

        self.state = "import"
        return {
            "name": _("Import stock quantities"),
            "type": "ir.actions.act_window",
            "res_model": "stock.import",
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def validate_data(self, reader, def_code_index, quantity_index):
        Product = self.env["product.product"]
        errors = []
        values = {}

        for i, row in enumerate(reader):
            try:
                product_code = row[def_code_index]
                product_qty = float(row[quantity_index])
            except ValueError as exc:
                raise UserError(
                    _(
                        "Invalid data in row %(row_number):\n"
                        "Internal Reference: '%(row_reference)'\n"
                        "Quantity: '%(row_quantity)'",
                        row_number=i,
                        row_reference=row[def_code_index],
                        row_quantity=row[quantity_index],
                    )
                ) from exc
            product = Product.search([("default_code", "=", product_code)])

            if not len(product):
                errors.append(
                    _(
                        "%s: Could not find product with this Internal Reference.",
                        product_code,
                    )
                )
                continue
            elif len(product) > 2:
                errors.append(
                    _(
                        "%s: Multiple products found with this Internal Reference.",
                        product_code,
                    )
                )
                continue

            values[product.id] = product_qty
        return errors, values

    def action_reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload",
        }
