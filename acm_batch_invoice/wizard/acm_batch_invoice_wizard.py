# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ACMBatchInvoiceWizard(models.TransientModel):
    _name = 'acm.batch.invoice.wizard'
    _description = 'Batch Invoice Wizard'

    date_invoice = fields.Date(
        default=fields.Date.today,
    )

    @api.multi
    def button_confirm(self):
        batch = self.env['acm.batch.invoice']
        context = dict(self._context or {})
        invoices = batch.browse(context.get('active_ids'))
        invoices.date_invoice = self.date_invoice
        return invoices.button_create_invoice()
