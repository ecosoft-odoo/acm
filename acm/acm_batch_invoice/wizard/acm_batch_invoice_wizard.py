# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class ACMBatchInvoiceWizard(models.TransientModel):
    _name = 'acm.batch.invoice.wizard'
    _description = 'Batch Invoice Wizard'

    date_invoice = fields.Date(
        string='Invoice Date',
        readonly=True,
    )

    @api.multi
    def button_confirm(self):
        active_ids = self._context.get('active_ids')
        batches = self.env['acm.batch.invoice'].browse(active_ids)
        return batches.button_create_invoice()
