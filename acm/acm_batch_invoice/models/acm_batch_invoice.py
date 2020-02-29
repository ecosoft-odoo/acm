# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from collections import namedtuple
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class ACMBatchInvoice(models.Model):
    _name = 'acm.batch.invoice'
    _description = 'ACM Batch Invoice'

    name = fields.Char(
        readonly=True,
        copy=False,
        help="Number of batch invoice",
    )
    invoice_type = fields.Selection(
        selection=[
            ('sale', 'Customer'),
        ],
        default='sale',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('done', 'Invoiced'),
        ],
        default='draft',
        required=True,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        default=fields.Date.today,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date Range',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain="[('type', '=', invoice_type)]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    water_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Water Product',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    electric_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Electric Product',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    batch_invoice_line_ids = fields.One2many(
        comodel_name='acm.batch.invoice.line',
        inverse_name='batch_invoice_id',
        string='Bill Invoice Lines',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    group_id = fields.Many2one(
        string='Zone',
        comodel_name='account.analytic.group',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    invoice_count = fields.Integer(
        compute='_compute_invoice_count',
    )

    @api.multi
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = \
                len(rec.batch_invoice_line_ids.mapped('invoice_id'))

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.invoice_count > 0:
                raise ValidationError(
                    _('As this batch already create invoice(s), '
                      'deletion is not allowed'))
            if rec.state != 'draft':
                raise UserError(
                    _('You cannot delete an batch invoice which is not draft ')
                )
        return super().unlink()

    @api.onchange('date_range_id', 'group_id')
    def _onchange_batch_invoice_is_create(self):
        exists = self.env['acm.batch.invoice'].search([
            ('date_range_id', '=', self.date_range_id.id),
            ('group_id', '=', self.group_id.id)])
        if exists:
            message = (_('Batch Invoice for %s, Zone %s already exists.\n'
                         'Are you sure to continue?') %
                       (self.date_range_id.name, self.group_id.name))
            warning = {
                'title': _('Warning'),
                'message': message,
            }
            return {'warning': warning}

    @api.multi
    def button_confirm(self):
        Sequene = self.env['ir.sequence']
        seq_code = 'acm.batch.invoice'
        for rec in self:
            if not rec.batch_invoice_line_ids:
                raise ValidationError(_('Meter Lines cannot be empty!'))
            if not rec.name:
                ctx = {'ir_sequence_date': rec.date_invoice}
                rec.name = Sequene.with_context(ctx).next_by_code(seq_code)
            # Check no negative amount
            rec.batch_invoice_line_ids._check_no_negative_amount()
        self.write({'state': 'confirm'})

    @api.multi
    def button_set_to_draft(self):
        self.write({'state': 'draft'})

    def action_view_invoice(self):
        tree_view = self.env.ref("account.invoice_tree")
        form_view = self.env.ref("account.invoice_form")
        val = self.env['account.invoice'].search(
            [('origin', '=', self.name)]
        )
        result = {
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            "views": [(tree_view.id, "tree"), (form_view.id, "form")],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', val.ids)],
            "context": {"create": False},
        }
        return result

    @api.model
    def _prepare_invoice_dict(self, line):
        batch = line.batch_invoice_id
        invoice = self.env['account.invoice'].new({
            'type': 'out_invoice',
            'type2': 'utility',
            'partner_id': line.partner_id.id,
            'origin': batch.name,
            'name': line.contract_id.rent_product_id.name,
            'currency_id': self.env.user.company_id.currency_id.id,
            'journal_id': batch.journal_id.id,
            'date_invoice': batch.date_invoice,
            'company_id': self.env.user.company_id.id,
            'user_id': self.env.user.id,
        })
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
    def _prepare_invoice_line_dict(self, type, line, invoice):
        line_vals = {'invoice_id': invoice.id}
        utility_info = line._get_utility_info(type)
        line_vals.update(utility_info)
        invoice_line = self.env['account.invoice.line'].new(line_vals)
        invoice_line._onchange_product_id()
        res = invoice_line._convert_to_write(invoice_line._cache)
        res.update(utility_info)  # Ensure untility_info
        res['account_analytic_id'] = line.contract_id.id  # Ensure contract
        return res

    @api.multi
    def _create_invoices(self):
        self.ensure_one()
        Invoice = self.env['account.invoice']
        utility_types = ['electric_amount', 'electric_amount_2',
                         'flat_rate', 'water_amount']
        for line in self.batch_invoice_line_ids:
            if not line.amount_subtotal:
                continue
            invoice_dict = self._prepare_invoice_dict(line)
            invoice = Invoice.create(invoice_dict)
            lines_dict = []
            for type in utility_types:
                if line[type]:  # If line has amount
                    lines_dict.append(
                        (0, 0, self._prepare_invoice_line_dict(type, line,
                                                               invoice)))
            invoice.write({'invoice_line_ids': lines_dict})
            invoice.compute_taxes()
            line.invoice_id = invoice

    @api.multi
    def button_create_invoice(self):
        self.ensure_one()
        self._create_invoices()
        self.write({'state': 'done'})
        return self.action_view_invoice()

    @api.model
    def _update_batch_invoice_line(self, contract, batch_invoice_line):
        batch_invoice = self.env['acm.batch.invoice'].search([
            ('state', '=', 'done'),
            ('group_id', '=', self.group_id.id),
            ('date_range_id.date_end', '<=', self.date_range_id.date_start),
        ], order="date_invoice desc", limit=1)
        line = batch_invoice.batch_invoice_line_ids.filtered(
            lambda l: l.contract_id == contract)
        batch_invoice_line.update({
            'flat_rate': line.flat_rate,
            'electric_from': line.electric_to,
            'electric_from_2': line.electric_to_2,
            'water_from': line.water_to,
        })

    @api.multi
    def _get_overlap(self, date_start, date_end):
        self.ensure_one()
        Range = namedtuple('Range', ['start', 'end'])
        r1 = Range(start=date_start, end=date_end)
        r2 = Range(start=self.date_range_id.date_start,
                   end=self.date_range_id.date_end)
        latest_start = max(r1.start, r2.start)
        earliest_end = min(r1.end, r2.end)
        delta = (earliest_end - latest_start).days + 1
        overlap = max(0, delta)
        return overlap

    @api.multi
    def retriveve_product_line(self):
        self.batch_invoice_line_ids = False
        if not self.batch_invoice_line_ids:
            contract = self.env['account.analytic.account'].search([
                ('group_id', '=', self.group_id.id),
            ])
            Batch_line = self.env['acm.batch.invoice.line']
            for line in contract:
                # Skip some contract as date not overlap with range date
                overlap = self._get_overlap(line.date_start, line.date_end)
                if not overlap:
                    continue
                lock_number = line.agreement_id.rent_product_id.lock_number
                batch_invoice_line = Batch_line.new(
                    {
                        'contract_id': line.id,
                        'lock_number': lock_number,
                        'partner_id': line.partner_id.id,
                    }
                )
                # Update batch invoice line
                # self._update_batch_invoice_line(line, batch_invoice_line)
                self.batch_invoice_line_ids += batch_invoice_line


class ACMBatchInvoiceLine(models.Model):
    _name = 'acm.batch.invoice.line'
    _description = 'ACM Batch Invoice Lines'
    _order = 'lock_number'

    batch_invoice_id = fields.Many2one(
        comodel_name='acm.batch.invoice',
        index=True,
        required=True,
        ondelete='cascade',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        ondelete='set null',
        readonly=True,
    )
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        required=True,
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
        readonly=True,
        required=True,
    )
    flat_rate = fields.Float(
        string='Electric Flat Rate',
    )
    lock_number = fields.Char(
        readonly=True,
        required=True,
    )
    water_amount = fields.Float(
        readonly=True,
        compute='_compute_all_amount',
        store=True,
    )
    water_from = fields.Float(
        digits=(12, 0),
    )
    water_to = fields.Float(
        digits=(12, 0),
    )
    electric_amount = fields.Float(
        string='#1 Electric Amount',
        compute='_compute_all_amount',
        readonly=True,
        store=True,
    )
    electric_from = fields.Float(
        string='#1 Electric From',
        digits=(12, 0),
    )
    electric_to = fields.Float(
        string='#1 Electric To',
        digits=(12, 0),
    )
    electric_amount_2 = fields.Float(
        string='#2 Electric Amount',
        compute='_compute_all_amount',
        readonly=True,
        store=True,
    )
    electric_from_2 = fields.Float(
        string='#2 Electric From',
        digits=(12, 0),
    )
    electric_to_2 = fields.Float(
        string='#2 Electric To',
        digits=(12, 0),
    )
    amount_subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_all_amount',
        readonly=True,
        store=True,
    )

    @api.depends('flat_rate', 'water_to', 'water_from', 'electric_from',
                 'electric_to', 'electric_from_2', 'electric_to_2')
    def _compute_all_amount(self):
        utility_types = ['water_amount', 'electric_amount',
                         'electric_amount_2', 'flat_rate']
        for rec in self:
            amount_subtotal = 0.0
            for type in utility_types:
                info = rec._get_utility_info(type)
                rec[type] = info['quantity'] * info['price_unit']
                amount_subtotal += rec[type]
            rec.amount_subtotal = amount_subtotal

    @api.multi
    def _check_no_negative_amount(self):
        field_lst = ['water_to', 'water_from', 'water_amount', 'electric_from',
                     'electric_to', 'electric_amount', 'electric_from_2',
                     'electric_to_2', 'electric_amount_2', 'flat_rate']
        for rec in self:
            for f in field_lst:
                if rec[f] < 0:
                    raise UserError(_('Negative amount is not allowed'))

    @api.multi
    def _get_utility_info(self, type):
        self.ensure_one()
        line = self
        batch = line.batch_invoice_id
        utilities = {
            'water_amount': {
                'product_id': batch.water_product_id.id,
                'name': _('ค่าน้ำประปา'),
                'meter_to': line.water_to,
                'meter_from': line.water_from,
                'quantity': line.water_to - line.water_from,
                'price_unit': batch.water_product_id.lst_price,
            },
            'electric_amount': {
                'product_id': batch.electric_product_id.id,
                'name': _('ค่าไฟฟ้า'),
                'meter_to': line.electric_to,
                'meter_from': line.electric_from,
                'quantity': line.electric_to - line.electric_from,
                'price_unit': batch.electric_product_id.lst_price,
            },
            'electric_amount_2': {
                'product_id': batch.electric_product_id.id,
                'name': _('ค่าไฟฟ้า (มิเตอร์ 2)'),
                'meter_to': line.electric_to_2,
                'meter_from': line.electric_from_2,
                'quantity': line.electric_to_2 - line.electric_from_2,
                'price_unit': batch.electric_product_id.lst_price,
            },
            'flat_rate': {
                'product_id': batch.electric_product_id.id,
                'name': _('ค่าไฟฟ้า (เหมาจ่าย)'),
                'quantity': 1,
                'price_unit': line.flat_rate,
            },
        }
        return utilities[type]
