# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementCreateInvoice(models.TransientModel):
    _name = 'agreement.create.invoice'

    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True,
    )
    agreement_line_ids = fields.Many2many(
        comodel_name='agreement.line',
        string='Agreement Lines',
    )
    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=fields.Date.today(),
    )
    count_agreement = fields.Integer(
        string='Count Agreement',
        compute='_compute_count_agreement',
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        active_ids = self._context.get('active_ids', [])
        agreements = self.env['agreement'].browse(active_ids)
        agreement_lines = agreements.mapped('line_ids').filtered(
            lambda l: l.product_id == self.product_id and
            l.date_start is False and l.date_end is False)
        return {
            'value': {'agreement_line_ids': agreement_lines, },
        }

    @api.depends('agreement_line_ids')
    def _compute_count_agreement(self):
        self.count_agreement = \
            len(list(set(self.agreement_line_ids.mapped('agreement_id'))))

    @api.multi
    def action_create_invoice(self):
        active_ids = self._context.get('active_ids', [])
        if self.count_agreement != len(active_ids):
            raise UserError(
                _('Agreement number is not valid with selected.'))
        if not self.count_agreement:
            raise UserError(_('No agreements.'))
        if len(list(set(self.agreement_line_ids.mapped('agreement_id')
                    .mapped('contract_type')))) > 1:
            raise UserError(_('Please select just one contract type.'))
        invoices = self.env['account.invoice']
        for line in self.agreement_line_ids:
            invoice = self.env['account.invoice'].create(
                self._prepare_invoice(line))
            invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
            if invoice_line_vals:
                self.env['account.invoice.line'].create(invoice_line_vals)
            invoice.compute_taxes()
            invoices |= invoice
            # Write start date and end date
            line.write({
                'date_start': self.date_invoice,
                'date_end': self.date_invoice,
                'invoiced': True,
            })
        # Return invoice view
        action = self.env.ref('account.action_invoice_tree1')
        if self.agreement_line_ids[0].agreement_id.contract_type == 'purchase':
            action = self.env.ref('account.action_vendor_bill_template')
        result = action.read()[0]
        result.update({
            'domain': [('id', 'in', invoices.ids)],
        })
        return result

    @api.multi
    def _prepare_invoice(self, line):
        self.ensure_one()
        journal = self.env['account.journal'].search(
            [('type', '=', line.agreement_id.contract_type),
             ('company_id', '=', line.agreement_id.company_id.id), ],
            limit=1, )
        if not journal:
            raise UserError(
                _("Please define a %s journal for the company '%s'.") %
                (line.agreement_id.contract_type,
                 line.agreement_id.company_id.name or '')
            )
        currency = (
            line.agreement_id.partner_id.property_product_pricelist.currency_id
            or line.agreement_id.company_id.currency_id
        )
        invoice_type = 'out_invoice'
        if line.agreement_id.contract_type == 'purchase':
            invoice_type = 'in_invoice'
        invoice = self.env['account.invoice'].new({
            'reference': line.agreement_id.code,
            'type': invoice_type,
            'partner_id': line.agreement_id.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': self.date_invoice,
            'origin': line.agreement_id.name,
            'company_id': line.agreement_id.company_id.id,
            'user_id': line.agreement_id.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.multi
    def _prepare_invoice_line(self, line, invoice_id):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.qty,
            'uom_id': line.uom_id.id,
        })
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update({
            'name': line.name,
            'price_unit': line.lst_price,
        })
        return invoice_line_vals
