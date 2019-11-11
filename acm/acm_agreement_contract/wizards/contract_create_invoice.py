# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class ContractCreateInvoice(models.TransientModel):
    _name = 'contract.create.invoice'

    @api.multi
    def action_create_invoices(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        contracts = self.env['account.analytic.account'].browse(active_ids)
        invoices = contracts.recurring_create_invoice()
        return self.view_invoices(contracts, invoices)

    @api.multi
    def view_invoices(self, contracts, invoices):
        self.ensure_one()
        if len(list(set(contracts.mapped('contract_type')))) > 1:
            return True
        action = self.env.ref(
            'contract.act_purchase_recurring_invoices')
        if contracts[0].contract_type == 'sale':
            action = self.env.ref(
                'contract.act_recurring_invoices')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % (invoices.ids)
        return result
