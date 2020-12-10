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
    )
    product_ids = fields.Many2many(
        comodel_name='product.product',
        string='Invoice Items',
        domain=lambda self: self._get_product_domain(),
        required=True,
    )

    @api.model
    def _get_product_domain(self):
        if self._context.get('active_model') != 'account.analytic.account':
            return []
        active_ids = self._context.get('active_ids', [])
        Contract = self.env['account.analytic.account']
        contracts = Contract.browse(active_ids)
        product_ids = contracts and \
            set(contracts[0].recurring_invoice_line_ids.
                filtered('manual').mapped('product_id').ids) or set()
        for contract in contracts:
            new_product_ids = set(contract.recurring_invoice_line_ids.
                                  filtered('manual').mapped('product_id').ids)
            product_ids = product_ids.intersection(new_product_ids)
        return [('id', 'in', list(product_ids))]

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
            'name': line.name,
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
            'type2': 'rent',
            'name': contract.rent_product_id.name,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
    def _create_manual_invoice(self, contract, date_invoice, products):
        # Can not create invoice after termination date
        termination_date = contract.agreement_id.termination_date
        if not contract.active:
            raise ValidationError(_("Can not create invoice of %s with inactive contract.") % contract.name)
        if termination_date and date_invoice > termination_date:
            raise ValidationError(_("Can not create invoice of %s after termination date.") % contract.name)
        # Create invoice
        invoice = self.env['account.invoice'].create(
            self._prepare_manaul_invoice(contract, date_invoice))
        lines = contract.recurring_invoice_line_ids.filtered(
            lambda l: l.manual and l.product_id in products)
        for line in lines:
            invoice_line_vals = self._prepare_manual_invoice_line(line,
                                                                  invoice.id)
            if invoice_line_vals:
                self.env['account.invoice.line'].create(invoice_line_vals)
        invoice.compute_taxes()
        return invoice

    @api.multi
    def _check_create_manual_invoice(self, contract, date_invoice, products):
        """
        This function for check
        1. Invoice don't created with same product and invoice date on the contract.
        2. Invoice don't created with same deposit and lum sum rent product on the contract.
        """
        self.ensure_one()
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']
        # For point 1
        invoices = Invoice.search([
            ('contract_id', '=', contract.id), ('state', '!=', 'cancel'),
            ('date_invoice', '=', date_invoice)])
        product_ids = invoices.mapped('invoice_line_ids.product_id').ids
        if set(products.ids).intersection(set(product_ids)):
            raise ValidationError(
                _('Invoice of %s created already.' % (contract.name, )))
        # For point 2 (Fix for KT)
        val_types = set(products.mapped('value_type'))
        if val_types.intersection(set(['lump_sum_rent', 'security_deposit'])):
            invoice_lines = InvoiceLine.search([
                ('invoice_id.state', '!=', 'cancel'),
                ('account_analytic_id', '=', contract.id),
                ('product_id', 'in', products.ids)])
            if invoice_lines:
                raise ValidationError(
                    _('Invoice of %s created already.' % (contract.name, )))

    @api.multi
    def action_create_manual_invoice(self):
        self.ensure_one()
        contracts = self.env['account.analytic.account'].\
            browse(self._context.get('active_ids'))
        invoices = self.env['account.invoice']
        for contract in contracts:
            # Check create manual invoice
            self._check_create_manual_invoice(
                contract, self.date_invoice, self.product_ids)
            # Create Manual Invoice
            invoice = self._create_manual_invoice(contract, self.date_invoice,
                                                  self.product_ids)
            invoices |= invoice
        return self.view_manual_invoice(contracts, invoices)

    @api.model
    def view_manual_invoice(self, contracts, invoices):
        if len(list(set(contracts.mapped('contract_type')))) > 1:
            return True
        action = self.env.ref(
            'contract.act_purchase_recurring_invoices')
        if contracts[0].contract_type == 'sale':
            action = self.env.ref(
                'contract.act_recurring_invoices')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % (invoices.ids)
        return result
