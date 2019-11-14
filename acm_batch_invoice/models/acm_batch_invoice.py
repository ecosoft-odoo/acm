# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        domain="[('type', '=', 'service')]",
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    electric_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Electric Product',
        domain="[('type', '=', 'service')]",
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
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        copy=False,
        store=True,
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
    def _prepare_invoice_line(self, invoice_id, line, product):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': product['product_id'],
            'name': product['name'],
            'meter_from': product['meter_from'],
            'meter_to': product['meter_to'],
            'quantity': product['qty'],
            'price_unit': product['amount'],
        })
        invoice_line._onchange_product_id()
        return invoice_line._convert_to_write(invoice_line._cache)

    @api.multi
    def _prepare_invoice(self):
        for inv in self.batch_invoice_line_ids:
            invoice = self.env['account.invoice'].new({
                'type': 'out_invoice',
                'partner_id': inv.partner_id.id,
                'batch_invoice_id': self.id,
                'currency_id': self.env.user.company_id.currency_id.id,
                'journal_id': self.journal_id.id,
                'date_invoice': self.date_invoice,
                'company_id': self.env.user.company_id.id,
                'user_id': self.env.user.id,
            })
            # Get other invoice values from partner onchange
            invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        for line in self.batch_invoice_line_ids:
            invoices = self.env['account.invoice'].create(
                self._prepare_invoice())
            water = {
                'product_id': self.water_product_id.id,
                'name': line.lock,
                'meter_from': line.water_from,
                'meter_to': line.water_to,
                'qty': line.water_to - line.water_from,
                'amount': line.water_amount,
            }
            water_product = self._prepare_invoice_line(invoices, line, water)
            electric = {
                'product_id': self.electric_product_id.id,
                'name': line.lock,
                'meter_from': line.electric_from,
                'meter_to': line.electric_to,
                'qty': line.electric_to - line.electric_from,
                'amount': line.electric_amount,
            }
            electric_product = self._prepare_invoice_line(
                invoices, line, electric
            )
            self.env['account.invoice.line'].create(
                (water_product, electric_product)
            )
            invoices.compute_taxes()

    @api.multi
    def button_create_invoice(self):
        self.ensure_one()
        self._create_invoice()
        self.write({'state': 'done'})
        return self.action_view_invoice()

    @api.multi
    def retriveve_product_line(self):
        if not self.batch_invoice_line_ids:
            agreement = self.env['agreement'].search([
                ('state', '=', 'active'),
                ('is_template', '=', False),
            ])
            Batch_line = self.env['acm.batch.invoice.line']
            for line in agreement:
                self.batch_invoice_line_ids += Batch_line.new(
                    {
                        'agreement_id': line.id,
                        'partner_id': line.partner_id.id,
                        'lock': line.rent_product_id.name,
                    }
                )


class ACMBatchInvoiceLine(models.Model):
    _name = 'acm.batch.invoice.line'
    _description = 'ACM Batch Invoice Lines'

    batch_invoice_id = fields.Many2one(
        comodel_name='acm.batch.invoice',
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreements'
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner',
    )
    lock = fields.Text()
    water_amount = fields.Float()
    water_from = fields.Float(
        string='Water From',
    )
    water_to = fields.Float(
        string='Water To',
    )
    electric_amount = fields.Float()
    electric_from = fields.Float(
        string='Electric From',
    )
    electric_to = fields.Float(
        string='Electric To',
    )

    @api.onchange('water_to', 'water_from', 'electric_to', 'electric_from')
    def _onchange_amount(self):
        water_diff = self.water_to - self.water_from
        water_price = self.batch_invoice_id.water_product_id.lst_price
        elec_diff = self.electric_to - self.electric_from
        elec_price = self.batch_invoice_id.electric_product_id.lst_price
        water_amount = water_diff * water_price
        electric_amount = elec_diff * elec_price
        self.water_amount = water_amount if water_amount > 0 else 0
        self.electric_amount = electric_amount if electric_amount > 0 else 0
