# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    type2 = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('utility', 'Utility'),
            ('toilet', 'Toilet'),
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
