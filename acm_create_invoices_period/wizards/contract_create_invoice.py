# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api, fields


class ContractCreateInvoice(models.TransientModel):
    _inherit = 'contract.create.invoice'

    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Period',
        index=True,
        copy=False,
    )

    @api.multi
    def view_invoices(self, contracts, invoices):
        self.ensure_one()
        # Update period
        invoices.write({'date_range_id': self.date_range_id.id})
        return super().view_invoices(contracts, invoices)
