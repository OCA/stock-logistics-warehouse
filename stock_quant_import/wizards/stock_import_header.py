from odoo import fields, models


class StockImportHeader(models.TransientModel):
    _name = "stock.import.header"
    _description = "Stock Import Header"

    name = fields.Char(string="Column Name")
    stock_import_id = fields.Many2one("stock.import")
