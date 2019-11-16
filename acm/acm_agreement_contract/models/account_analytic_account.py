# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
        ondelete='restrict',
        readonly=True,
    )
    rent_product_id = fields.Many2one(
        comodel_name='product.product',
        compute='_compute_product_id',
        string='Product',
        store=True,
    )
    group_id = fields.Many2one(
        string='Zone',
    )

    @api.constrains('recurring_invoice_line_ids')
    def _check_recurring_invoice_line_ids(self):
        for rec in self:
            lines = rec.recurring_invoice_line_ids
            rent_products = \
                lines.filtered(lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            if len(rent_products) > 1:
                raise UserError(_('Only one rental product is allowed.'))

    @api.depends('recurring_invoice_line_ids')
    @api.multi
    def _compute_product_id(self):
        for rec in self:
            rent_product = rec.recurring_invoice_line_ids.filtered(
                lambda l: l.product_id.value_type == 'rent') \
                .mapped('product_id')
            if rent_product:
                rec.rent_product_id = rent_product[0]

    @api.model
    def _prepare_invoice_line(self, line, invoice_id):
        next_date = line.analytic_account_id.recurring_next_date
        if not (line.date_start or line.date_end):
            return {}
        if line.date_start and not line.date_end and \
           line.date_start > next_date:
            return {}
        if line.date_end and not line.date_start and next_date > line.date_end:
            return {}
        if not(line.date_start <= next_date <= line.date_end):
            return {}
        return super(AccountAnalyticAccount, self) \
            ._prepare_invoice_line(line, invoice_id)

    @api.multi
    def recurring_create_invoice(self):
        """Create invoice only if Invoice contain some lines."""
        invoices = super().recurring_create_invoice()
        no_line_invs = invoices.filtered(lambda inv: not inv.invoice_line_ids)
        invoices -= no_line_invs
        no_line_invs.unlink()
        return invoices

    @api.multi
    def _create_invoice(self, invoice=False):
        invoice = super()._create_invoice(invoice=invoice)
        # Update invoice type
        invoice.write({
            'type2': 'rent',
        })
        return invoice
