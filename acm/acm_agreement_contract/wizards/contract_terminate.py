# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ContractTerminateLine(models.TransientModel):
    _name = 'contract.terminate.line'

    terminate_id = fields.Many2one(
        comodel_name='contract.terminate',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    qty = fields.Float(
        string='Quantity',
        default=1,
    )
    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Unit of Measure',
        required=True,
    )
    lst_price = fields.Float(
        string='Unit Price',
    )
    invoice_type = fields.Selection(
        selection=[
            ('out_invoice', 'Customer Invoice'),
            ('in_invoice', 'Vendor Bill'), ],
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.uom_id = self.product_id.uom_id.id
        self.lst_price = self.product_id.lst_price


class ContractTerminate(models.TransientModel):
    _name = 'contract.terminate'

    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
        default='lessee',
        required=True,
    )
    date_termination_requested = fields.Date(
        string='Termination Requested Date',
        required=True,
    )
    date_termination = fields.Date(
        string='Termination Date',
        required=True,
    )
    reason_termination = fields.Text(
        string='Termination Reason',
        required=True,
    )
    lessee_terminate_line_ids = fields.One2many(
        comodel_name='contract.terminate.line',
        inverse_name='terminate_id',
        domain=[('invoice_type', '=', 'out_invoice')],
    )
    lessor_terminate_line_ids = fields.One2many(
        comodel_name='contract.terminate.line',
        inverse_name='terminate_id',
        domain=[('invoice_type', '=', 'in_invoice')],
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        default=lambda self: self._context.get('active_id'),
    )

    @api.multi
    def action_terminate_contract(self):
        self.ensure_one()
        context = self._context.copy()
        agreement_id = context.get('active_id', [])
        agreement = self.env['agreement'].browse(agreement_id)
        if agreement.state != 'active':
            raise UserError(_('Agreement is not active.'))
        if agreement.is_contract_create is False:
            raise UserError(_('Contract is not active.'))
        # if self.date_termination > fields.Date.today():
        #     raise UserError(
        #         _('Termination Date cannot more than Current Date'))
        agreement.write({
            'is_termination': True,
            'termination_by': self.termination_by,
            'termination_requested': self.date_termination_requested,
            'termination_date': self.date_termination,
            'reason_termination': self.reason_termination,
        })
        # Create Invoice
        invoice_ids = []
        if self.lessee_terminate_line_ids:
            invoice1 = \
                self.with_context(invoice_type='out_invoice')._create_invoice()
            invoice_ids.append(invoice1.id)
        if self.lessor_terminate_line_ids:
            invoice2 = \
                self.with_context(invoice_type='in_invoice')._create_invoice()
            invoice_ids.append(invoice2.id)
        if invoice_ids:
            return {
                'name': _('Invoices'),
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', invoice_ids)],
            }
        agreement.inactive_statusbar()
        return agreement

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        journal = self.env['account.journal'].search([
                ('type', '=', self.agreement_id.contract_type),
                ('company_id', '=', self.agreement_id.company_id.id)], limit=1)
        if not journal:
            raise UserError(
                _("Please define a %s journal for the company '%s'.") %
                (self.agreement_id.contract_type,
                 self.agreement_id.company_id.name or '')
            )
        currency = (
            self.agreement_id.partner_id.property_product_pricelist.currency_id
            or self.agreement_id.company_id.currency_id
        )
        invoice = self.env['account.invoice'].new({
            'reference': self.agreement_id.code,
            'type': self._context.get('invoice_type'),
            'partner_id': self.agreement_id.partner_id.address_get(
                ['invoice'])['invoice'],
            'currency_id': currency.id,
            'journal_id': journal.id,
            'date_invoice': self.date_termination,
            'origin': self.agreement_id.name,
            'company_id': self.agreement_id.company_id.id,
            'user_id': self.agreement_id.partner_id.user_id.id,
        })
        # Get other invoice values from partner onchange
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
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

    @api.multi
    def _create_invoice(self):
        self.ensure_one()
        context = self._context.copy()
        invoice = self.env['account.invoice'].create(
            self._prepare_invoice())
        lines = self.env['contract.terminate.line']
        if context.get('invoice_type') == 'out_invoice':
            lines = self.lessee_terminate_line_ids
        else:
            lines = self.lessor_terminate_line_ids
        for line in lines:
            invoice_line_vals = self._prepare_invoice_line(line, invoice.id)
            if invoice_line_vals:
                self.env['account.invoice.line'].create(invoice_line_vals)
        invoice.compute_taxes()
        return invoice
