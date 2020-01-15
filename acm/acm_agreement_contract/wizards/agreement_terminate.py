# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementTerminate(models.TransientModel):
    _name = 'agreement.terminate'
    _description = 'Terminate Agreement'

    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
        default='lessee',
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
    attachment_ids = fields.One2many(
        comodel_name='agreement.terminate.attachment',
        inverse_name='terminate_id',
        string='Attachment',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
        domain=lambda self: self._get_domain_product_id(),
    )
    amount = fields.Float(
        string='Amount',
    )
    date_invoice = fields.Date(
        string='Bill Date',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        domain=lambda self: self._get_domain_journal_id(),
    )

    @api.model
    def _get_products(self, agreements, type=''):
        products = agreements.mapped('line_ids').filtered(
            lambda l: l.product_id.value_type == type).mapped('product_id')
        return products

    @api.model
    def default_get(self, fields_list):
        res = super(AgreementTerminate, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(active_ids)
        if len(agreements) <= 1:
            products = self._get_products(agreements, type='security_deposit')
            if len(products) <= 1:
                res['product_id'] = products.id
        journal = self.env['account.journal'].search(
            self._get_domain_journal_id())
        if len(journal) > 1:
            journal = journal[0]
        res.update({
            'journal_id': journal.id,
        })
        return res

    @api.model
    def _get_domain_product_id(self):
        active_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(active_ids)
        products = self._get_products(agreements, type='security_deposit')
        return [('id', 'in', products.ids)]

    @api.model
    def _get_domain_journal_id(self):
        return [('type', '=', 'purchase'),
                ('company_id', '=', self.env.user.company_id.id)]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        active_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(active_ids)
        if len(agreements) <= 1:
            contracts = agreements._search_contract()
            invoices = self.env['account.invoice'].search(
                [('state', '=', 'paid'), ('contract_id', 'in', contracts.ids)])
            invoice_lines = invoices.mapped('invoice_line_ids').filtered(
                lambda l: l.product_id == self.product_id)
            self.amount = sum(invoice_lines.mapped('price_subtotal'))

    @api.model
    def _prepare_invoice(self, agreement):
        invoice = self.env['account.invoice'].new({
            'type': 'in_invoice',
            'partner_id': agreement.partner_id.id,
            'origin': agreement.name,
            'name': agreement.rent_product_id.name,
            'currency_id': self.env.user.company_id.currency_id.id,
            'journal_id': self.journal_id.id,
            'date_invoice': self.date_invoice,
            'company_id': self.env.user.company_id.id,
            'user_id': self.env.user.id,
        })
        invoice._onchange_partner_id()
        return invoice._convert_to_write(invoice._cache)

    @api.model
    def _prepare_invoice_line(self, agreement, invoice):
        agreement_line = agreement.line_ids.filtered(
            lambda l: l.product_id == self.product_id)
        if len(agreement_line) > 1:
            agreement_line = agreement_line[0]
        contract = agreement._search_contract()
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice.id,
            'product_id': self.product_id.id,
            'quantity': agreement_line.qty,
            'uom_id': agreement_line.uom_id.id,
        })
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update({
            'name': agreement_line.name,
            'account_analytic_id': contract.id,
            'price_unit': self.amount,
        })
        return invoice_line_vals

    @api.model
    def _create_invoice(self, agreement):
        invoice = self.env['account.invoice'].create(
            self._prepare_invoice(agreement))
        self.env['account.invoice.line'].create(
            self._prepare_invoice_line(agreement, invoice))
        invoice.compute_taxes()
        return invoice

    @api.multi
    def action_terminate_agreement(self):
        """
        Step to termination agreement
        1. Create vendor bill
        2. Attach file in agreement (if any)
        3. Terminate agreement (Change state from active to inactive)
        """
        Agreement = self.env['agreement']
        agreements = Agreement.browse(self._context.get('active_ids', []))
        agreements.ensure_one()
        for agreement in agreements:
            agreement._validate_contract_create()
            agreement.write({
                'is_terminate': True,
                'termination_by': self.termination_by,
                'termination_date': self.date_termination,
                'reason_termination': self.reason_termination,
            })
            # Create vendor bill
            if self.product_id:
                if not self.amount:
                    raise UserError(_('Please specify security deposit.'))
                self._create_invoice(agreement)
            # Create attachment
            for attachment in self.attachment_ids:
                self.env['ir.attachment'].create({
                    'name': attachment.filename,
                    'datas': attachment.file,
                    'datas_fname': attachment.filename,
                    'res_model': 'agreement',
                    'res_id': agreement.id,
                    'type': 'binary',
                })
        return agreements


class AgreementTerminateAttachment(models.TransientModel):
    _name = 'agreement.terminate.attachment'

    file = fields.Binary(
        string='File',
        required=True,
    )
    filename = fields.Char(
        string='File Name',
    )
    terminate_id = fields.Many2one(
        comodel_name='agreement.terminate',
        string='Terminate',
    )
