# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

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
            ('done', 'Invoice'),
        ],
        default='draft',
        required=True,
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        states={'done': [('readonly', True)]},
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
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    electric_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Electric Product',
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
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        copy=False,
        store=True,
    )
    group_id = fields.Many2one(
        string='Zone',
        comodel_name='account.analytic.group',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def button_confirm(self):
        for rec in self:
            if not rec.batch_invoice_line_ids:
                raise ValidationError(_('Meter Lines are empty.'))
            if not rec.name:
                rec.name = (
                    self.env["ir.sequence"]
                    .with_context(ir_sequence_date=rec.date_invoice)
                    .next_by_code("acm.batch.invoice")
                )
            rec.write({'state': 'confirm'})

    @api.multi
    def button_set_to_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})

    def action_view_invoice(self):
        tree_view = self.env.ref("account.invoice_tree")
        form_view = self.env.ref("account.invoice_form")
        val = self.env['account.invoice'].search(
            [('batch_invoice_id', '=', self.id)]
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

    @api.multi
    def _prepare_product(
            self, invoice, product, name, meter_from, meter_to, amount, analy):
        val = {
            'product_id': product,
            'name': name,
            'meter_from': meter_from if meter_to - meter_from != 0 else '-',
            'meter_to': meter_to if meter_to - meter_from != 0 else '-',
            'qty': meter_to - meter_from if meter_to - meter_from != 0 else 1,
            'amount': amount,
            'analytic': analy,
        }
        return self._prepare_invoice_line(invoice, val)

    @api.multi
    def _prepare_invoice_line(self, invoice_id, product):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': product['product_id'],
            'meter_from': product['meter_from'],
            'meter_to': product['meter_to'],
            'quantity': product['qty'],
            'price_unit': product['amount'],
            'account_analytic_id': product['analytic'],
        })
        invoice_line._onchange_product_id()
        invoice_line._convert_to_write(invoice_line._cache)
        line = self.env['account.invoice.line'].create(
            invoice_line._convert_to_write(invoice_line._cache)
        )
        if product['name'] == 'ค่าไฟฟ้าเหมาจ่าย':
            line.write({'price_unit': product['amount']})
        line.write({'name': product['name']})
        return invoice_id.compute_taxes()

    @api.multi
    def _prepare_invoice(self, partner):
        for inv in self:
            invoice = self.env['account.invoice'].new({
                'type': 'out_invoice',
                'partner_id': partner,
                'batch_invoice_id': self.id,
                'currency_id': self.env.user.company_id.currency_id.id,
                'journal_id': self.journal_id.id,
                'date_invoice': self.date_invoice,
                'company_id': self.env.user.company_id.id,
                'user_id': self.env.user.id,
                'type2': 'utility',
            })
            # Get other invoice values from partner onchange
            invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        for line in self.batch_invoice_line_ids:
            if line.check_condition() is False:
                continue
            invoices = self.env['account.invoice'].create(
                self._prepare_invoice(line.partner_id.id))
            if line.water_amount != 0:
                self._prepare_product(
                    invoices, self.water_product_id,
                    self.water_product_id.name, line.water_from,
                    line.water_to, line.water_amount,
                    line.contract_id,
                )
            if line.electric_amount != 0:
                self._prepare_product(
                    invoices, self.electric_product_id,
                    self.electric_product_id.name, line.electric_from,
                    line.electric_to, line.electric_amount,
                    line.contract_id,
                )
            if line.electric_amount_2 != 0:
                self._prepare_product(
                    invoices, self.electric_product_id,
                    self.electric_product_id.name, line.electric_from_2,
                    line.electric_to_2, line.electric_amount_2,
                    line.contract_id,
                )
            if line.flat_rate != 0:
                self._prepare_product(
                    invoices, self.electric_product_id,
                    'ค่าไฟฟ้าเหมาจ่าย', 0,
                    0, line.flat_rate,
                    line.contract_id,
                )

    @api.multi
    def button_create_invoice(self):
        self.ensure_one()
        self._create_invoice()
        self.write({'state': 'done'})
        return self.action_view_invoice()

    @api.multi
    def retriveve_product_line(self):
        self.batch_invoice_line_ids = False
        if not self.batch_invoice_line_ids:
            contract = self.env['account.analytic.account'].search([
                ('group_id', '=', self.group_id.id)
            ])
            Batch_line = self.env['acm.batch.invoice.line']
            for line in contract:
                lock_number = line.agreement_id.rent_product_id.lock_number
                self.batch_invoice_line_ids += Batch_line.new(
                    {
                        'contract_id': line.id,
                        'lock_number': lock_number,
                        'partner_id': line.partner_id.id,
                    }
                )


class ACMBatchInvoiceLine(models.Model):
    _name = 'acm.batch.invoice.line'
    _description = 'ACM Batch Invoice Lines'

    batch_invoice_id = fields.Many2one(
        comodel_name='acm.batch.invoice',
    )
    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
    )
    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    flat_rate = fields.Float(
    )
    lock_number = fields.Char()
    water_amount = fields.Float(
        readonly=True,
        compute='_compute_water_amount',
    )
    water_from = fields.Float(
        digits=(12, 0),
    )
    water_to = fields.Float(
        digits=(12, 0),
    )
    electric_amount = fields.Float(
        readonly=True,
        compute='_compute_electric_amount',
    )
    electric_from = fields.Float(
        digits=(12, 0),
    )
    electric_to = fields.Float(
        digits=(12, 0),
    )
    electric_amount_2 = fields.Float(
        readonly=True,
        compute='_compute_electric_amount_2',
    )
    electric_from_2 = fields.Float(
        digits=(12, 0),
    )
    electric_to_2 = fields.Float(
        digits=(12, 0),
    )

    @api.constrains(
        'electric_amount_2', 'electric_amount', 'water_amount', 'flat_rate')
    def _check_all_amount(self):
        for amount in self:
            if (amount.flat_rate or amount.electric_amount_2 or
                    amount.electric_amount or amount.water_amount) < 0:
                raise UserError(
                    _("Negative amount is not allowed, please check"))

    @api.depends('water_to', 'water_from')
    def _compute_water_amount(self):
        for rec in self:
            water_diff = rec.water_to - rec.water_from
            water_price = rec.batch_invoice_id.water_product_id.lst_price
            rec.water_amount = water_diff*water_price

    @api.depends('electric_to', 'electric_from')
    def _compute_electric_amount(self):
        for rec in self:
            elec_diff = rec.electric_to - rec.electric_from
            elec_price = rec.batch_invoice_id.electric_product_id.lst_price
            rec.electric_amount = elec_diff * elec_price

    @api.depends('electric_to_2', 'electric_from_2')
    def _compute_electric_amount_2(self):
        for rec in self:
            elec_diff = rec.electric_to_2 - rec.electric_from_2
            elec_price = rec.batch_invoice_id.electric_product_id.lst_price
            rec.electric_amount_2 = elec_diff * elec_price

    @api.multi
    def check_condition(self):
        if not (self.water_amount or self.electric_amount
                or self.electric_amount_2 or self.flat_rate):
            return False
