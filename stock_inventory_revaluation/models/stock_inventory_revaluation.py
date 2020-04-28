# Copyright 2020 Matt Taylor
# Copyright 2016-17 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
#   (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class StockInventoryRevaluation(models.Model):

    _name = 'stock.inventory.revaluation'
    _description = 'Inventory revaluation'

    name = fields.Char(
        string='Reference',
        help="Reference for the journal entry",
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        default='/')

    reval_template_id = fields.Many2one(
        comodel_name='stock.inventory.revaluation.template',
        string='Template',
        readonly=True,
        help="Choose a template to automatically apply revaluation options.",
        states={'draft': [('readonly', False)]})

    revaluation_type = fields.Selection(
        selection=[
            ('price_change', 'Unit Price Change'),
            ('inventory_value', 'Total Value Change'),
        ],
        string="Revaluation Type",
        readonly=True, required=True,
        default='inventory_value',
        help="'Unit Price Change': Change the per-unit price of the product. "
             "Inventory value is recalculated according to the new price and "
             "available quantity.\n"
             "'Total Value Change': Change the total value of the inventory. "
             "Unit price is recalculated according to the new total value and "
             "available quantity.  Actual resulting value may be slightly "
             "different, based on per-unit price precision and rounding.",
        states={'draft': [('readonly', False)]})

    remarks = fields.Text(
        string='Remarks',
        help="Displays by default Inventory Revaluation. This text is copied "
             "to the journal entry.",
        readonly=True,
        states={'draft': [('readonly', False)]})

    state = fields.Selection(
        selection=[('draft', 'Draft'),
                   ('posted', 'Posted'),
                   ('cancel', 'Cancelled')],
        string='Status',
        readonly=True,
        required=True,
        default='draft')

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        readonly=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.inventory.revaluation'),
        states={'draft': [('readonly', False)]})

    document_date = fields.Datetime(
        string='Applied date',
        readonly=True)

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="Select a journal for the accounting entry.  Leave blank to use"
             "the default journal for the product.")

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        required=True,
        domain=[('type', '=', 'product')],
        states={'draft': [('readonly', False)]},
        readonly=True)

    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template',
        related='product_id.product_tmpl_id',
        store=True)

    cost_method = fields.Char(
        string="Cost Method",
        related='product_id.cost_method')

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='UoM',
        related="product_template_id.uom_id")

    old_cost = fields.Float(
        string='Old cost',
        help='Displays the previous cost of the product',
        digits=dp.get_precision('Product Price'),
        readonly=True)

    current_cost = fields.Float(
        string='Current cost',
        related='product_id.standard_price',
        help='The current cost of the product.')

    new_cost = fields.Float(
        string='New cost',
        help="Enter the new cost you wish to assign to the product. Relevant "
             "only when the selected revaluation type is Price Change.",
        digits=dp.get_precision('Product Price'),
        readonly=True,
        states={'draft': [('readonly', False)]})

    current_value = fields.Float(
        string='Current value',
        related='product_id.stock_value',
        help='Total current value of product in stock')

    old_value = fields.Float(
        string='Old value',
        help='Total current value of the product, prior to revaluation',
        digits=dp.get_precision('Account'),
        readonly=True)

    new_value = fields.Float(
        string='New value',
        help="New total value for the available inventory. Relevant only if "
             "the selected revaluation type is Total Value Change.  Actual "
             "resulting value may be slightly different, based on per-unit "
             "price precision and rounding.",
        digits=dp.get_precision('Account'),
        readonly=True,
        states={'draft': [('readonly', False)]})

    qty_available = fields.Float(
        string='Quantity On Hand',
        related='product_id.qty_available',
        digits=dp.get_precision('Product Unit of Measure'))

    increase_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Increase Account',
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The Increase "
             "Account is used when the inventory value is increased due to "
             "the revaluation.",
        states={'draft': [('readonly', False)]},
        readonly=True)

    decrease_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Decrease Account',
        help="Define the G/L accounts to be used as the balancing account in "
             "the transaction created by the revaluation. The Decrease "
             "Account is used when the inventory value is decreased.",
        states={'draft': [('readonly', False)]},
        readonly=True)

    stock_valuation_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Valuation Account',
        help="To be set automatically when posting the revaluation",
        readonly=True)

    account_move_ids = fields.One2many(
        comodel_name='account.move',
        inverse_name='stock_inventory_revaluation_id',
        readonly=True)

    post_date = fields.Date(
        string='Posting Date',
        help="Journal Entry posting date",
        states={'draft': [('readonly', False)]},
        readonly=True)

    reval_move_ids = fields.One2many(
        comodel_name='stock.inventory.revaluation.move',
        inverse_name='revaluation_id',
        string='Revaluation Moves',
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False)

    @api.constrains('new_value', 'new_cost')
    def _check_new_cost(self):
        account_prec = self.env['decimal.precision'].precision_get('Account')
        for rec in self:
            if float_compare(rec.new_value, 0.0,
                             precision_digits=account_prec) < 0:
                raise UserError(_("The new value must be positive"))
            if float_compare(rec.new_cost, 0.0,
                             precision_digits=account_prec) < 0:
                raise UserError(_("The new cost must be positive"))

    @api.onchange("product_id")
    def _onchange_product_product_id(self):
        if self.product_id and not self.reval_template_id:
            self.increase_account_id = self.product_id.categ_id and \
                self.product_id.categ_id.\
                property_inventory_revaluation_increase_account_categ
            self.decrease_account_id = self.product_id.categ_id and \
                self.product_id.categ_id.\
                property_inventory_revaluation_decrease_account_categ

    @api.onchange("reval_template_id")
    def _onchange_reval_template_id(self):
        self._load_template_parameters()

    @api.model
    def _load_all_valued_moves(self, new_cost):
        self.ensure_one()
        wiz = self.env['stock.inventory.revaluation.get.moves'].create({
            'revaluation_id': self.id,
        })
        wiz.process()
        for move in self.reval_move_ids:
            move.new_value = move.qty * new_cost

    @api.model
    def _load_template_parameters(self):
        """Load template parameters into the revaluation.  We always
        overwrite the revaluation type.  Other fields are only set if they
        are empty."""
        if self.reval_template_id:
            self.revaluation_type = \
                self.reval_template_id.revaluation_type
            if not self.journal_id:
                self.journal_id = \
                    self.reval_template_id.journal_id
            if not self.increase_account_id:
                self.increase_account_id = \
                    self.reval_template_id.increase_account_id
            if not self.decrease_account_id:
                self.decrease_account_id = \
                    self.reval_template_id.decrease_account_id
            if not self.remarks:
                self.remarks = \
                    self.reval_template_id.remarks

    @api.model
    def _validate_product_parameters(self):
        if self.product_id.product_tmpl_id.type != 'product':
            raise UserError(_("Only stockable products can be revalued"))

        product_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if float_compare(self.product_id.qty_available, 0.0,
                         precision_digits=product_prec) <= 0:
            raise UserError(_("The available quantity for this product "
                              "must be a positive number"))

        if self.product_id.cost_method == 'fifo' and \
                self.revaluation_type == 'price_change':
            raise UserError(_("Revaluation type 'Unit Price Change' doesn't "
                              "apply to Stock-Move-Specific changes.  Use "
                              "type 'Total Value Change'."))

        if self.product_id.cost_method in ['standard', 'average']:
            if self.revaluation_type == 'price_change':
                if self.current_cost == self.new_cost:
                    raise UserError(_("Change the cost before posting"))
            else:
                if self.current_value == self.new_value:
                    raise UserError(_("Change the value before posting"))

    @api.model
    def _validate_fifo_moves(self):
        if not self.reval_move_ids:
            raise UserError(_("Please revalue one or more stock moves"))

        prec = self.env['decimal.precision'].precision_get('Account')
        abs_change = sum(
            [abs(x.new_value - x.current_value) for x in self.reval_move_ids]
        )
        if float_compare(abs_change, 0.0, precision_digits=prec) == 0:
            raise UserError(_("No changes were made to move values"))

        move_products = self.reval_move_ids.mapped('product_id.id')
        if not all(x == self.product_id.id for x in move_products):
            raise UserError(_("The selected moves are for a different "
                              "product than the revaluation"))

    @api.model
    def _set_validate_accounting_parameters(self):
        """Set and validate accounting fields, in preparation to post"""
        if not self.decrease_account_id or not self.increase_account_id:
            raise UserError(
                _("Please add an Increase Account and a Decrease Account to "
                  "the revaluation, or add them to product category %s") %
                self.product_template_id.categ_id.name)
        if not self.post_date:
            self.post_date = fields.Date.today()
        acc = self.product_template_id.get_product_accounts()
        if not acc.get('stock_valuation'):
            raise UserError(_("Please add a Stock Valuation Account in "
                              "product category %s") %
                            self.product_template_id.categ_id.name)
        self.stock_valuation_account_id = acc['stock_valuation']
        self.journal_id = self.journal_id or acc.get('stock_journal')
        if not self.journal_id:
            raise UserError(_("Please specify an accounting journal on the "
                              "revaluation, or in product category %s") %
                            self.product_template_id.categ_id.name)

    @api.multi
    def post(self):
        for reval in self:
            reval._load_template_parameters()
            reval._validate_product_parameters()

            if reval.product_id.cost_method in ['standard', 'average']:
                reval.old_cost = reval.current_cost
                reval.old_value = reval.current_value
                if reval.revaluation_type == 'price_change':
                    reval.new_value = reval.qty_available * reval.new_cost
                    reval.product_id.with_context(
                        force_company=reval.company_id.id
                    ).sudo().write({'standard_price': reval.new_cost})
                else:
                    reval.new_cost = reval.new_value / reval.qty_available
                    reval.product_id.with_context(
                        force_company=reval.company_id.id
                    ).sudo().write({'standard_price': reval.new_cost})

                reval._load_all_valued_moves(reval.new_cost)

            elif reval.product_id.cost_method == 'fifo':
                reval._validate_fifo_moves()

            else:
                raise UserError(_("Unknown costing method %s" %
                                  reval.product_id.cost_method))

            reval.reval_move_ids.write_new_value()
            if reval.product_id.categ_id.property_valuation == 'real_time':
                reval._set_validate_accounting_parameters()
                reval.reval_move_ids.sudo().create_account_moves()

            reval.document_date = fields.Datetime.now()
            reval.post_date = reval.post_date or reval.document_date
            reval.state = 'posted'

    @api.model
    def create(self, values):
        sequence_obj = self.env['ir.sequence']
        if values.get('name', '/') == '/':
            values['name'] = sequence_obj.next_by_code(
                'stock.inventory.revaluation')
        return super(StockInventoryRevaluation, self).create(values)

    @api.multi
    def button_post(self):
        self.post()
        return True

    @api.multi
    def button_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.model
    def _validate_cancel_moves(self):
        # If the remaining quantity at the time of cancellation is different,
        # from the current quantity, we can't allow the cancellation.
        product_prec = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        abs_change = sum(
            [abs(x.qty - x.old_qty) for x in self.reval_move_ids]
        )
        if float_compare(abs_change, 0.0,
                         precision_digits=product_prec) != 0:
            raise UserError(
                _("The remaining quantity on a stock move has changed. You "
                  "can't cancel this revaluation. Try creating a new "
                  "revaluation to reverse this one."))

    @api.multi
    def button_cancel(self):
        for reval in self:
            reval._validate_cancel_moves()
            reval.reval_move_ids.write_old_value()
            if reval.product_id.cost_method in ['standard', 'average']:
                reval.product_id.with_context(
                    force_company=reval.company_id.id
                ).sudo().write({'standard_price': reval.old_cost})
            if reval.account_move_ids:
                # cancel the account moves
                reval.account_move_ids.sudo().button_cancel()
                # delete the account moves
                # Note: the corresponding move_lines and move_reconciles will
                # be automatically deleted too
                reval.account_move_ids.sudo().with_context(
                    revaluation=True).unlink()
            reval.state = 'cancel'
        return True


class StockInventoryRevaluationMove(models.Model):
    """This model was previously named stock.inventory.revaluation.quant.
    Quant indicates a specific stock quantity of the same product that
    entered your warehouse at a specific moment in time, in one specific
    operation, and in a single lot, if lot tracking is enabled.  The purpose
    of the stock.quant model has changed in recent versions of Odoo,
    and valuation is no longer assigned to the quant. The fifo cost
    information is now stored in the stock.move model.  Stock moves store a
    total remaining value for all move lines.  That means we can't specify a
    remaining value for individual lots in the move lines."""

    _name = 'stock.inventory.revaluation.move'
    _description = 'Inventory Revaluation Move'

    revaluation_id = fields.Many2one(
        comodel_name='stock.inventory.revaluation',
        string='Revaluation',
        required=True,
        readonly=True)

    state = fields.Selection(related='revaluation_id.state')

    move_id = fields.Many2one(
        comodel_name='stock.move',
        string='Stock Move',
        required=True,
        readonly=True)

    name = fields.Char(
        string="Name",
        compute='_compute_name',
        store=True,
        readonly=True)

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        related="move_id.product_id")

    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        related="move_id.location_dest_id")

    qty = fields.Float(
        string='Quantity',
        related="move_id.remaining_qty")

    in_date = fields.Datetime(
        string='Incoming Date',
        related="move_id.date")

    current_value = fields.Float(
        string='Current Value',
        related="move_id.remaining_value")

    old_qty = fields.Float(
        string='Old Quantity',
        readonly=True,
        help="We store the remaining quantity, at the time of posting the "
             "revaluation, in case the revaluation gets canceled. If the "
             "remaining quantity at the time of cancellation is different, "
             "we can't allow the cancellation.")

    old_value = fields.Float(
        string='Previous Value',
        help='Shows the previous value of the move',
        digits=dp.get_precision('Product Price'),
        readonly=True)

    new_value = fields.Float(
        string='New Value',
        help="Enter the new value you wish to assign to the Move. Relevant "
             "only when the selected revaluation type is Total Value Change.",
        digits=dp.get_precision('Product Price'),
        copy=False)

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related="revaluation_id.company_id")

    @api.constrains('new_value')
    def _check_value_positive(self):
        for rec in self:
            if rec.new_value < 0.0:
                raise ValidationError(_('The new value must be positive'))

    @api.depends('move_id')
    def _compute_name(self):
        for move in self:
            if not move.move_id or not move.product_id:
                move.name = 'NEW'
            else:
                move.name = move.move_id.reference
                if not move.product_id.tracking == 'none':
                    lot_names = move.move_id.\
                        mapped('move_line_ids.lot_id.name')
                    move.name = "%s: %s" % (
                        move.name, ", ".join(lot_names))

    @api.model
    def get_value_change(self):
        self.ensure_one()
        amount_diff = self.new_value - self.current_value
        return amount_diff

    @api.model
    def write_new_value(self):
        # Note: we always set the fifo `remaining_value` field no matter
        # which cost method is used, to ease the switching of cost method.
        # We do not update the `price_unit` field. For details, see the
        # _run_fifo() and _run_valuation() methods in stock_account:
        # odoo/addons/stock_account/models/stock.py
        for reval_move in self:
            reval_move.old_value = reval_move.current_value
            reval_move.old_qty = reval_move.qty
            reval_move.move_id.sudo().write({
                'remaining_value': reval_move.new_value,
            })
        return True

    @api.model
    def write_old_value(self):
        # If the remaining quantity at the time of cancellation is different,
        # from the current quantity, we can't allow the cancellation.
        for reval_move in self:
            reval_move.move_id.sudo().write({
                'remaining_value': reval_move.old_value,
            })
        return True

    @api.model
    def _prepare_account_move_data(self):
        return {
            'narration': self.revaluation_id.remarks,
            'date': self.revaluation_id.post_date,
            'ref': self.revaluation_id.name,
            'journal_id': self.revaluation_id.journal_id.id,
            'stock_inventory_revaluation_id': self.revaluation_id.id,
            'stock_move_id': self.move_id.id,
        }

    @api.model
    def _prepare_debit_move_line_data(self, move, amount, account_id):
        return {
            'name': self.revaluation_id.name,
            'date': move.date,
            'product_id': self.product_id.id,
            'account_id': account_id,
            'move_id': move.id,
            'debit': amount,
            'quantity': self.qty,
        }

    @api.model
    def _prepare_credit_move_line_data(self, move, amount, account_id):
        return {
            'name': self.revaluation_id.name,
            'date': move.date,
            'product_id': self.product_id.id,
            'account_id': account_id,
            'move_id': move.id,
            'credit': amount,
            'quantity': self.qty,
        }

    @api.model
    def create_account_moves(self):
        """Must be called after writing new values to reval moves"""
        prec = self.env['decimal.precision'].precision_get('Account')
        stock_account_id = self[0].revaluation_id.stock_valuation_account_id.id
        increase_account_id = self[0].revaluation_id.increase_account_id.id
        decrease_account_id = self[0].revaluation_id.decrease_account_id.id

        for line in self:
            amount_diff = line.new_value - line.old_value
            if float_compare(amount_diff, 0.0, precision_digits=prec) == 0:
                continue

            acc_move_data = line._prepare_account_move_data()
            acc_move = line.env['account.move'].create(acc_move_data)

            if float_compare(amount_diff, 0.0, precision_digits=prec) < 0:
                debit_account_id = decrease_account_id
                credit_account_id = stock_account_id
            else:
                debit_account_id = stock_account_id
                credit_account_id = increase_account_id

            move_line_data = line._prepare_debit_move_line_data(
                acc_move,
                abs(amount_diff),
                debit_account_id)
            self.env['account.move.line'].with_context(
                {'check_move_validity': False}).create(move_line_data)

            move_line_data = line._prepare_credit_move_line_data(
                acc_move,
                abs(amount_diff),
                credit_account_id)
            self.env['account.move.line'].create(move_line_data)

            acc_move.post()
