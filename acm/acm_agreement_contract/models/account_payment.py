# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    description = fields.Char(
        string='Reference/Description',
        compute='_compute_description',
    )
    narration = fields.Text(
        string='Narration',
        copy=False,
    )

    @api.multi
    def _compute_description(self):
        for rec in self:
            description_list = list(set(filter(
                lambda k: k != '',
                [x.name and x.name.strip() or '' for x in rec.invoice_ids])))
            rec.description = ', '.join(description_list)
