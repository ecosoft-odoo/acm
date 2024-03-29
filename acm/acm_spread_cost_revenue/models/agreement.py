# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class Agreement(models.Model):
    _inherit = 'agreement'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if vals.get('termination_date'):
            contracts = self.with_context(active_test=False)._search_contract()
            invoices = self.env['account.invoice'].search([('contract_id', 'in', contracts.ids)])
            spread_lines = invoices.mapped('invoice_line_ids.spread_id.line_ids')
            # If terminate agreement, date on spreed lines after termination date will be termination date
            spread_lines = spread_lines.filtered(lambda l: l.date > vals['termination_date'] and not l.move_id)
            spread_lines.write({'date': vals['termination_date']})
        return res
