# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class Agreement(models.Model):
    _inherit = 'agreement'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('termination_date'):
            contracts = self.with_context(active_test=False)._search_contract()
            invoices = self.env['account.invoice'].search([('contract_id', 'in', contracts.ids)])
            spread_lines = invoices.mapped('invoice_line_ids.spreed_id.line_ids')
            # If terminate agreement, date on spreed lines after today date will be termination date
            spread_lines = spread_lines.filtered(lambda l: l.date > fields.Date.today() and l.move_id is False)
            spread_lines.write({'date': vals['termination_date']})
        return res
