# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
from datetime import datetime
import json


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    type2 = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('service', 'Service'),
            ('utility', 'Utility'),
            ('toilet', 'Toilet'),
            ('sale', 'Sale'),
            ('others', 'Others'),
        ],
        string='Invoice Type',
    )
    groups = fields.Char(
        compute='_compute_groups',
        string='Zone',
        store=True,
    )
    is_merge = fields.Boolean(
        string='Merged',
        default=False,
    )
    payment_date = fields.Char(        
        compute='_compute_payment_date',
        string='Pay Date',
    )
    
    @api.depends('payments_widget')
    def _compute_payment_date(self):
        for invoice in self:
            payment_data = json.loads(invoice.payments_widget)
            if payment_data and isinstance(payment_data, dict):
                try:
                    # Picking 'date' in the first item of the list 'content'
                    date_str = payment_data.get('content', [{}])[0].get('date', '')
                    if date_str:
                        # Convert date from 'YYYY-MM-DD' to 'DD/MM/YYYY'
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        invoice.payment_date = date_obj.strftime('%d/%m/%Y')
                    else:
                        invoice.payment_date = ''
                except (json.JSONDecodeError, TypeError, KeyError):
                    invoice.payment_date = ''
            else:
                invoice.payment_date = ''

    @api.multi
    def _get_computed_reference(self):
        self.ensure_one()
        if self.company_id.invoice_reference_type == 'invoice_number':
            return self.number
        return super()._get_computed_reference()

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_groups(self):
        for rec in self:
            groups = list(set(rec.invoice_line_ids.mapped('group_id.name')))
            groups.sort()
            rec.groups = ', '.join(groups)

    @api.multi
    def action_invoice_cancel(self):
        res = super().action_invoice_cancel()
        if self._context.get('is_merge'):
            self.write({'is_merge': True})
        return res

    @api.model
    def _get_invoice_key_cols(self):
        invoice_key = super()._get_invoice_key_cols()
        invoice_key.append('type2')
        return invoice_key

    @api.model
    def _get_first_invoice_fields(self, invoice):
        vals = super()._get_first_invoice_fields(invoice)
        vals['type2'] = invoice.type2
        return vals


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='account_analytic_id.group_id',
        string='Zone',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        related='analytic_account_id.group_id',
        string='Zone',
    )
