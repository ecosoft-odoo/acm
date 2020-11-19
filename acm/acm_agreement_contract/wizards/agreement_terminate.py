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
    is_attachment = fields.Boolean(
        string='Attachment ?',
        default=False,
    )
    attachment_ids = fields.One2many(
        comodel_name='agreement.terminate.attachment',
        inverse_name='terminate_id',
        string='Attachment',
    )
    refund_deposit_type = fields.Selection(
        selection=[
            ('refund_deposit', 'Refund Deposit'),
            ('no_refund_deposit', 'No Refund Deposit'),
        ],
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
        string='Date',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
    )
    ref = fields.Char(
        string='Reference',
    )
    description = fields.Text(
        string='Description',
    )

    @api.onchange('refund_deposit_type')
    def _check_refund_deposit_type(self):
        domain = []
        if self.refund_deposit_type:
            active_id = self._context.get('active_id')
            agreement = self.env['agreement'].browse(active_id)
            security_deposit = agreement.line_ids.filtered(
                lambda l: l.product_id.value_type == 'security_deposit'
            )
            if not security_deposit:
                raise UserError(
                    _('Agreement "%s" have not security deposit.') %
                    agreement.name
                )
            if self.refund_deposit_type == 'refund_deposit':
                domain = [('type', '=', 'purchase')]
            else:
                domain = [('type', '=', 'general')]
        return {'domain': {'journal_id': domain}}

    @api.model
    def default_get(self, fields_list):
        res = super(AgreementTerminate, self).default_get(fields_list)
        active_ids = self._context.get('active_ids')
        agreements = self.env['agreement'].browse(active_ids)
        # Make sure no have multiple agreements
        agreements.ensure_one()
        agreement_lines = agreements.line_ids.filtered(
            lambda l: l.product_id.value_type == 'security_deposit')
        if len(agreement_lines) == 1:
            res.update({
                'product_id': agreement_lines[0].product_id.id,
                'amount': agreement_lines[0].lst_price,
            })
        return res

    @api.model
    def _get_domain_product_id(self):
        products = self.env['product.product'].search(
            [('value_type', '=', 'security_deposit')])
        return [('id', 'in', products.ids)]

    @api.multi
    def _prepare_invoice(self, agreement):
        self.ensure_one()
        if self.journal_id.type != 'purchase':
            raise UserError(
                _('This journal is not supported for create vendor bills.'))
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

    @api.multi
    def _prepare_invoice_line(self, agreement, invoice):
        self.ensure_one()
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
            'name': self.description,
            'account_analytic_id': contract.id,
            'price_unit': self.amount,
        })
        return invoice_line_vals

    @api.multi
    def _create_invoice(self, agreement):
        self.ensure_one()
        invoice = self.env['account.invoice'].create(
            self._prepare_invoice(agreement))
        self.env['account.invoice.line'].create(
            self._prepare_invoice_line(agreement, invoice))
        invoice.compute_taxes()
        return invoice

    @api.multi
    def _prepare_move(self, agreement):
        self.ensure_one()
        contract = agreement._search_contract()
        debit_account_id = self.journal_id.default_debit_account_id.id
        credit_account_id = self.journal_id.default_credit_account_id.id
        if not debit_account_id or not credit_account_id:
            raise UserError(_('Wrong journal !!'))
        return {
            'date': self.date_invoice,
            'ref': self.ref,
            'journal_id': self.journal_id.id,
            'line_ids': [
                (0, 0, {
                    'name': agreement.name,
                    'account_id': debit_account_id,
                    'debit': self.amount,
                    'credit': 0.0,
                    'partner_id': agreement.partner_id.id,
                    'analytic_account_id': contract.id,
                }),
                (0, 0, {
                    'name': agreement.name,
                    'account_id': credit_account_id,
                    'debit': 0.0,
                    'credit': self.amount,
                    'partner_id': agreement.partner_id.id,
                    'analytic_account_id': contract.id,
                })
            ]
        }

    @api.multi
    def _create_move(self, agreement):
        self.ensure_one()
        move = self.env['account.move'].create(self._prepare_move(agreement))
        # Post move
        move.post()
        return move

    @api.multi
    def action_terminate_agreement(self):
        """
        Step to termination agreement
        1. Create vendor bill
        2. Attach file in agreement (if any)
        3. Terminate agreement (Change state from active to inactive)
        """
        self.ensure_one()
        Agreement = self.env['agreement']
        agreements = Agreement.browse(self._context.get('active_ids', []))
        agreements.ensure_one()
        security_deposit = agreements.line_ids.filtered(
            lambda l: l.product_id.value_type == 'security_deposit'
        )
        if self.amount > security_deposit.lst_price:
            raise UserError(
                _('Maximum amount is "%d".') %
                security_deposit.lst_price
            )
        for agreement in agreements:
            agreement._validate_contract_create()
            # Create vendor bill
            invoice = self.env['account.invoice']
            move = self.env['account.move']
            if self.refund_deposit_type:
                if not self.amount:
                    raise UserError(_('Please specify security deposit.'))
                if self.refund_deposit_type == 'refund_deposit':
                    invoice = self._create_invoice(agreement)
                else:
                    move = self._create_move(agreement)
            agreement.write({
                'is_terminate': True,
                'termination_by': self.termination_by,
                'termination_date': self.date_termination,
                'reason_termination': self.reason_termination,
                'invoice_id': invoice.id,
                'move_id': move.id,
            })
            # Create attachment
            if self.is_attachment:
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
    _description = 'Agreement Terminated Attachment'

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
