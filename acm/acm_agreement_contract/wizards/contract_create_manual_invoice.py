# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ContractCreateManualInvoice(models.TransientModel):
    _name = 'contract.create.manual.invoice'
    _description = 'Create One Manual Invoice From Contract'

    date_invoice = fields.Date(
        string='Invoice Date',
        required=True,
        default=lambda self: fields.Date.today(),
    )
    analytic_invoice_line_id = fields.Many2one(
        comodel_name='account.analytic.invoice.line',
        string='Select Line',
        required=True,
        domain=[('manual', '=', True)],
    )

    @api.model
    def _prepare_manual_invoice_line(self, line, invoice_id):
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice_id,
            'product_id': line.product_id.id,
            'quantity': line.quantity,
            'uom_id': line.uom_id.id,
            'discount': line.discount,
        })
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        contract = line.analytic_account_id
        invoice_line_vals.update({
            'account_analytic_id': contract.id,
            'price_unit': line.price_unit,
        })
        return invoice_line_vals

    @api.model
    def _prepare_manaul_invoice(self, contract, date_invoice):
        if not contract.partner_id:
            if contract.contract_type == 'purchase':
                raise ValidationError(
                    _("You must first select a Supplier for Contract %s!") %
                    contract.name)
            else:
                raise ValidationError(
                    _("You must first select a Customer for Contract %s!") %
                    contract.name)
        journal = contract.journal_id or self.env['account.journal'].search([
            ('type', '=', contract.contract_type),
            ('company_id', '=', contract.company_id.id)
        ], limit=1)
        if not journal:
            raise ValidationError(
                _("Please define a %s journal for the company '%s'.") %
                (contract.contract_type, contract.company_id.name or '')
            )
        currency = (
            contract.pricelist_id.currency_id or
            contract.partner_id.property_product_pricelist.currency_id or
            contract.company_id.currency_id
        )
        invoice_type = 'out_invoice'
        if contract.contract_type == 'purchase':
            invoice_type = 'in_invoice'
        invoice = self.env['account.invoice'].new({
            'reference': contract.code,
            'type': invoice_type,
            'partner_id': contract.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': date_invoice,
            'origin': contract.name,
            'company_id': contract.company_id.id,
            'contract_id': contract.id,
            'user_id': contract.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
    def _create_manual_invoice(self, contract, date_invoice, line):
        invoice = self.env['account.invoice'].create(
            self._prepare_manaul_invoice(contract, date_invoice))
        invoice_line_vals = self._prepare_manual_invoice_line(line, invoice.id)
        if invoice_line_vals:
            self.env['account.invoice.line'].create(invoice_line_vals)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def action_create_manual_invoice(self):
        self.ensure_one()
        contract = self.env['account.analytic.account'].\
            browse(self._context.get('active_id'))
        invoice = self._create_manual_invoice(contract, self.date_invoice,
                                              self.analytic_invoice_line_id)
        self.analytic_invoice_line_id.write({
            'date_start': invoice.date_invoice,
            'date_end': invoice.date_invoice,
        })
        return self.view_manual_invoice(contract, invoice)

    @api.model
    def view_manual_invoice(self, contract, invoice):
        action = self.env.ref(
            'contract.act_purchase_recurring_invoices')
        if contract.contract_type == 'sale':
            action = self.env.ref(
                'contract.act_recurring_invoices')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = [('id', '=', invoice.id)]
        return result
