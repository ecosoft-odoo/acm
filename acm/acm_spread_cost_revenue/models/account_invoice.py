# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        """ Also create the spread table if template is set.
        """
        for invoice in self:
            # Before validation, do create spread table on this invoice line
            for line in invoice.invoice_line_ids:
                template = line.product_id.spread_template_id
                if not template:
                    continue
                wizard = self.env['account.spread.invoice.line.link.wizard'].new({
                    'invoice_line_id': line.id,
                    'company_id': invoice.company_id.id,
                    'spread_action_type': 'template',
                    'template_id': template.id,
                })
                if template.spread_type != wizard.spread_type:
                    raise UserError(
                        _('Invalid template spread type (sale/purchase)'))
                ctx = {'spread_over': line.product_id.spread_over,
                       'account_analytic_id': line.account_analytic_id.id}
                wizard.with_context(ctx).confirm()
        return super().action_invoice_open()
