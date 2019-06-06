# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    purchase_evaluation_id = fields.Many2one(
        'product.cost.evaluation.history',
    )


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def product_cost_history_evaluation(self):
        incomplete_invoice_msg = _('Incomplete invoice Data')
        for inventory in self:
            for line in inventory.line_ids:
                # if line.purchase_evaluation_id:
                #     continue
                product_id = line.product_id
                vals = dict(
                    date_evaluation=inventory.date,  # todo date_inventory
                    product_id=product_id.id,
                    standard_cost=product_id.standard_price,
                    product_qty=line.product_qty,
                    lot_id=line.prod_lot_id.id,
                    list_price=product_id.lst_price,
                    name='',
                )
                # standard cost and list price already done
                # fifo and average needs only incoming moves
                incoming_domain = [
                    ('company_id', '=', self.env.user.company_id.id),
                    ('date', '<=', self.date),  # todo self.date_inventory or
                    ('state', '=', 'done'),
                    ('product_id', '=', line.product_id.id),
                    ('location_id.usage', '!=', 'internal'),
                    ('location_dest_id.usage', '=', 'internal'),
                ]
                all_domain = [
                    ('company_id', '=', self.env.user.company_id.id),
                    ('date', '<=', self.date),  # todo self.date_inventory or
                    ('state', '=', 'done'),
                    ('product_id', '=', line.product_id.id),
                    '|',
                    ('location_id.usage', '=', 'internal'),
                    ('location_dest_id.usage', '=', 'internal'),
                ]
                res_incoming = self.price_calculation(line, 'average',
                                                      incoming_domain)
                # match has:
                # product_id, product_qty, price_unit, product_qty_from (?)
                # purchase_price_unit, invoice_data_incomplete
                # average cost
                price_amount = product_qty = purchase_amount = 0
                for match in res_incoming:
                    price_amount += match[1] * match[2]
                    product_qty += match[1]
                    purchase_amount += match[1] * match[4]
                if product_qty != 0.0:
                    if not match[5]:
                        vals['average_cost'] = price_amount / product_qty
                    else:
                        vals['name'] += incomplete_invoice_msg
                    vals['average_purchase_cost'] = (
                        purchase_amount / product_qty)
                # fifo
                res_incoming = self.price_calculation(
                    line, 'fifo', incoming_domain)
                price_amount = product_qty = purchase_amount = 0
                for match in res_incoming:
                    price_amount += match[1] * match[2]
                    product_qty += match[1]
                    purchase_amount += match[1] * match[4]
                if product_qty != 0.0:
                    if not match[5]:
                        vals['fifo_cost'] = price_amount / product_qty
                    else:
                        if incomplete_invoice_msg not in vals['name']:
                            vals['name'] += incomplete_invoice_msg
                    vals['fifo_purchase_cost'] = purchase_amount / product_qty
                # lifo needs incoming and outgoing moves
                res_all = self.price_calculation(line, 'lifo', all_domain)
                price_amount = product_qty = purchase_amount = 0
                for match in res_all:
                    price_amount += match[1] * match[2]
                    product_qty += match[1]
                    purchase_amount += match[1] * match[4]
                if product_qty != 0.0:
                    if not match[5]:
                        vals['lifo_cost'] = price_amount / product_qty
                    else:
                        if incomplete_invoice_msg not in vals['name']:
                            vals['name'] += incomplete_invoice_msg
                    vals['lifo_purchase_cost'] = purchase_amount / product_qty
                res = self.env["product.cost.evaluation.history"].create(vals)
                line.purchase_evaluation_id = res.id

    @api.multi
    def price_calculation(self, line, evaluation_type, domain):
        order = 'date desc, id desc'
        move_obj = self.env['stock.move']
        move_ids = move_obj.search(domain, order=order)
        tuples = []
        qty_to_go = line.product_qty
        older_qty = line.product_qty
        invoice_data_incomplete = False
        # get only move with lot of inventory line
        flag = False
        for move in move_ids:
            for move_line in move.move_line_ids.filtered(
                lambda x: x.lot_id == line.prod_lot_id
            ):
                # Convert to UoM of product each time
                uom_from = move.product_uom
                qty_from = move_line.qty_done
                product_qty = uom_from._compute_quantity(
                    qty_from, move.product_id.uom_id)
                # Get price from purchase line
                purchase_price_unit = 0
                price_unit = 0
                if move.purchase_line_id:
                    if move.purchase_line_id.invoice_lines:
                        # this ones are linked to in invs
                        # invoice_line_id and move.invoice_line_id.\
                        # only linked to out invs
                        # invoice_id.state in ('open', 'paid'):
                        # todo get average price from invoice lines? yes
                        inv_lines = move.purchase_line_id.invoice_lines.\
                            filtered(lambda x: x.invoice_id.state in [
                                'open', 'paid'])
                        price_unit = sum(l.price_subtotal for l in inv_lines)\
                            / sum(l.quantity for l in inv_lines)
                    else:
                        # FIXME set price_unit = 0 for line
                        invoice_data_incomplete = True
                    # get price from purchase line
                    purchase_price_unit = \
                        move.purchase_line_id.price_subtotal / \
                        move.purchase_line_id.product_qty
                # FIXME set purchase_price to standard_price when missing?
                # else:
                #     # Get price from product, move is an inventory or not
                #     # linked to a purchase (income move created and even
                #     # invoiced, but price is not usable here)
                #     price_unit = move.product_id.standard_price

                if evaluation_type == 'fifo':
                    if qty_to_go - product_qty >= 0:
                        tuples.append((move.product_id.id, product_qty,
                                       price_unit, qty_from,
                                       purchase_price_unit,
                                       invoice_data_incomplete))
                        qty_to_go -= product_qty
                    else:
                        tuples.append((
                            move.product_id.id, qty_to_go, price_unit,
                            qty_from * qty_to_go / product_qty,
                            purchase_price_unit,
                            invoice_data_incomplete))
                        flag = True
                        break
                if evaluation_type == 'lifo':
                    # sale
                    if move.location_id.usage == 'internal' and \
                            move.location_dest_id.usage != 'internal':
                        older_qty += product_qty
                    # purchase
                    if move.location_id.usage != 'internal' and \
                            move.location_dest_id.usage == 'internal':
                        older_qty -= product_qty
                        if qty_to_go > older_qty > 0:
                            tuples.append((move.product_id.id,
                                           qty_to_go - older_qty, price_unit,
                                           qty_from, purchase_price_unit,
                                           invoice_data_incomplete))
                            qty_to_go = older_qty
                        elif qty_to_go > older_qty <= 0:
                            tuples.append((move.product_id.id, qty_to_go,
                                           price_unit,
                                           qty_from * qty_to_go / product_qty,
                                           purchase_price_unit,
                                           invoice_data_incomplete))
                            flag = True
                            break
                if evaluation_type == 'average':
                    tuples.append((move.product_id.id, product_qty,
                                   price_unit, qty_from, purchase_price_unit,
                                   invoice_data_incomplete))
            if flag:
                break
        return tuples
