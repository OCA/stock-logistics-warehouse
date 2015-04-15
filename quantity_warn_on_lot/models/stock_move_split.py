# -*- coding: utf-8 -*-

from openerp.osv import orm
from openerp.tools.translate import _


class InvalidAmountException(Exception):

    """
    InvalidAmountException is raised when there is not enough products.

    It contains the product_id, prodlot_id and the actual quantity of
    products after a successful update.
    """

    def __init__(self, product_id, prodlot_id, quantity):
        """
        Create the InvalidAmountException object.

        :params product_id: The product in question
        :params prodlot_id: The prodlot in question
        :params quantity: The quantity of products available
        """
        self.product_id = product_id
        self.prodlot_id = prodlot_id
        self.quantity = quantity


class StockMoveSplit(orm.TransientModel):

    """StockMoveSplit override to handle the amount of available products."""

    _inherit = 'stock.move.split'

    def get_confirm_view_id(self, cr, uid, context=None):
        """Get the default view id for the confirm view."""
        ir_model_data = self.pool.get('ir.model.data')
        view_ref = ir_model_data.get_object_reference(
            cr, uid, 'quantity_warn_on_lot', 'view_confirm_split'
        )
        return view_ref and view_ref[1] or False

    def restore_split(self, cr, uid, ids, context=None):
        """Restore the split to where we were before the warning."""
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move.split',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'nodestroy': True,
            'context': context,
        }

        active_id = context.get('active_id')
        move = self.pool['stock.move'].browse(cr, uid, active_id)
        picking = move.picking_id

        picking.message_post(
            "Pressed correct button in the confirmation window"
        )

        return res

    def continue_split(self, cr, uid, ids, context=None):
        """Continue splitting without and silence the warning."""
        if context is None:
            context = {}

        # Adding continue_split to the context will silence
        # the check for amount_quantity
        context['continue_split'] = True

        active_id = context.get('active_id')
        move = self.pool['stock.move'].browse(cr, uid, active_id)
        picking = move.picking_id

        picking.message_post(
            "Pressed continue button in the confirmation window"
        )

        return self.split_lot(cr, uid, ids, context=context)

    def fields_view_get(
        self, cr, uid,
        view_id=None, view_type='form',
        context=None, toolbar=False,
        submenu=False
    ):
        """Override the confirm_view and add a custom message."""
        base_func = super(StockMoveSplit, self).fields_view_get
        ret = base_func(cr, uid, view_id, view_type, context=context)

        view_confirm_id = self.get_confirm_view_id(cr, uid, context)

        if view_confirm_id == view_id:
            # Edit only the confirm window
            message = context.get('warning_message', '')
            # Simple and dirty replace {message} by our text
            ret['arch'] = ret['arch'].replace('{message}', message)

        return ret

    def split_lot(self, cr, uid, ids, context=None):
        """
        Override the split_lot method and handle errors.

        In case the available quantity is below 0, the split
        method will raise an InvalidAmountException. This method
        catch this error and instead open a new view that requires
        confirmation to continue the split or keep editing.

        Before returning this method, we have to rollback changes to
        be certain that none of the change made before raising the
        error will get saved to the database.
        """
        base_func = super(StockMoveSplit, self).split_lot

        try:
            res = base_func(cr, uid, ids, context=context)
        except InvalidAmountException as exc:
            # Prevent changes to be saved
            cr.rollback()

            view_id = self.get_confirm_view_id(cr, uid, context)

            message = _(
                "The remaining amount of <b>%(product_name)s</b> in the lot "
                "<b>%(lot_number)s</b> of the product isn't enough."
                "The remaining amount of products in this lot number is "
                "<b>%(quantity)d</b>."
                "Please correct your sale order"
            )

            format_dict = {
                "product_name": exc.product_id.name,
                "lot_number": exc.prodlot_id.name,
                "quantity": exc.quantity,
            }

            context['warning_message'] = message % format_dict

            # Call the window
            res = {
                'type': 'ir.actions.act_window',
                'view_id': view_id,
                'res_model': 'stock.move.split',
                'res_id': ids[0],
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'nodestroy': True,
                'context': context,
            }

        return res

    def split(self, cr, uid, ids, move_ids, context=None):
        """Check for the available stock quantity to be over 0."""
        if context is None:
            context = {}

        base_func = super(StockMoveSplit, self).split
        res = base_func(cr, uid, ids, move_ids, context)

        for data in self.browse(cr, uid, ids, context=context):
            for move in data.line_exist_ids:
                sum_in_draft = [
                    m.product_qty
                    for m in move.prodlot_id.move_ids
                    if m.state == 'draft' and m.id not in move_ids
                ]

                quantity_rest = (
                    move.prodlot_id.stock_available - sum(sum_in_draft)
                )

                if quantity_rest < 0 and not context.get('continue_split'):
                    raise InvalidAmountException(
                        move.prodlot_id.product_id,
                        move.prodlot_id, quantity_rest
                    )

        return res
