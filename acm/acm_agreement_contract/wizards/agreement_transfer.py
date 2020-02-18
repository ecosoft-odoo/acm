# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AgreementTransfer(models.TransientModel):
    _name = 'agreement.transfer'
    _description = 'Transfer Agreement'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='New Lessee',
        required=True,
    )
    partner_contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Primary Contact',
        help='The primary partner contact (If Applicable).',
    )
    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
    )
    date_contract = fields.Date(
        string='Contract Date',
        required=True,
    )
    date_termination = fields.Date(
        string='Termination Date',
        required=True,
    )
    termination_by = fields.Selection(
        selection=[
            ('lessee', 'Lessee'),
            ('lessor', 'Lessor'), ],
        string='Termination By',
        required=True,
    )
    reason_termination = fields.Text(
        string='Termination Reason',
        required=True,
    )
    is_refund_deposit = fields.Boolean(
        string='Refund Deposit ?',
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
    attachment_ids = fields.One2many(
        comodel_name='agreement.transfer.attachment',
        inverse_name='transfer_id',
        string='Attachment',
        domain=[('type', '=', 'old')],
    )
    attachment2_ids = fields.One2many(
        comodel_name='agreement.transfer.attachment',
        inverse_name='transfer_id',
        string='Attachment',
        domain=[('type', '=', 'new')],
    )

    @api.model
    def default_get(self, fields_list):
        res = super(AgreementTransfer, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(active_ids)
        if len(agreements) <= 1:
            res['date_end'] = agreements.end_date
        journal = self.env['account.journal'].search(
            self._get_domain_journal_id())
        if len(journal) <= 1:
            res['journal_id'] = journal.id
        res.update({
            'termination_by': 'lessee',
            'reason_termination': 'Transfer leasehold rights',
        })
        return res

    @api.model
    def _get_domain_product_id(self):
        products = self.env['product.product'].search(
            [('value_type', '=', 'security_deposit')])
        return [('id', 'in', products.ids)]

    @api.model
    def _get_domain_journal_id(self):
        return [('type', '=', 'purchase'),
                ('company_id', '=', self.env.user.company_id.id)]

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
        contract = agreement._search_contract()
        invoice_line = self.env['account.invoice.line'].new({
            'invoice_id': invoice.id,
            'product_id': self.product_id.id,
            'quantity': 1,
            'uom_id': self.product_id.uom_id.id,
        })
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        invoice_line_vals.update({
            'name': self.product_id.description or self.product_id.name,
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
    def action_transfer_agreement(self):
        """
        Step to transfer agreement
        1. Create new agreement
        (change lessee, contract date, start date and end date)
        2. Create vendor bill (refund security deposit to old lessee)
        3. Attach file in agreement (if any)
        4. Terminate old agreement (Change state from active to inactive)
        """
        if self.date_termination >= self.date_start:
            raise UserError(_('Termination date is no more than start date.'))
        Agreement = self.env['agreement']
        agreements = Agreement.browse(self._context.get('active_ids', []))
        agreements.ensure_one()
        new_agreements = Agreement
        for agreement in agreements:
            if not agreement.is_contract_create:
                raise UserError(
                    _('Please create contract %s.' % (agreement.name, )))
            agreement = agreement.with_context({
                'partner_id': self.partner_id.id,
                'partner_contact_id': self.partner_contact_id.id,
                'date_contract': self.date_contract,
                'date_start': self.date_start,
                'date_end': self.date_end,
            })
            new_agreement = agreement.create_agreement()
            new_agreements |= new_agreement
            # Write old agreement
            agreement.write({
                'is_transfer': True,
                'termination_date': self.date_termination,
                'termination_by': self.termination_by,
                'reason_termination': self.reason_termination,
            })
            # Create vendor bill for refund security deposit
            if self.is_refund_deposit:
                if not self.amount:
                    raise UserError(_('Please specify security deposit.'))
                self._create_invoice(agreement)
            # Create attachment
            for attachment in self.attachment_ids + self.attachment2_ids:
                self.env['ir.attachment'].create({
                    'name': attachment.filename,
                    'datas': attachment.file,
                    'datas_fname': attachment.filename,
                    'res_model': 'agreement',
                    'res_id': attachment.type == 'new' and new_agreement.id
                    or agreement.id,
                    'type': 'binary',
                })
        return new_agreements.view_agreement()


class AgreementTransferAttachment(models.TransientModel):
    _name = 'agreement.transfer.attachment'
    _description = 'Agreement Transfer Attachment'

    file = fields.Binary(
        string='File',
        required=True,
    )
    filename = fields.Char(
        string='File Name',
    )
    type = fields.Selection(
        selection=[
            ('old', 'Old Agreement Attachment'),
            ('new', 'New Agreement Attachment'),
        ],
        string='Type',
    )
    transfer_id = fields.Many2one(
        comodel_name='agreement.transfer',
        string='Transfer',
    )
