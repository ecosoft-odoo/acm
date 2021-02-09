# Copyright 2021 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class ACMBatchInvoice(models.Model):
    _inherit = "acm.batch.invoice"

    @api.model
    def _prepare_invoice_dict(self, line):
        res = super()._prepare_invoice_dict(line)
        res["date_range_id"] = line.batch_invoice_id.date_range_id.id
        return res
