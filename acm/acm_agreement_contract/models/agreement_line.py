# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class AgreementLine(models.Model):
    _inherit = 'agreement.line'

    qty = fields.Float(
        default=1,
    )
    lst_price = fields.Float(
        string='Unit Price',
    )
    date_start = fields.Date(
        string='Start Date',
    )
    date_end = fields.Date(
        string='End Date',
    )
    invoiced = fields.Boolean()

    @api.multi
    def prepare_contract_line(self):
        return {
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.qty,
            'uom_id': self.uom_id.id,
            'specific_price': self.lst_price,
            'date_start': self.date_start,
            'date_end': self.date_end,
        }

    @api.onchange("product_id")
    def _onchange_product_id(self):
        super()._onchange_product_id()
        self.lst_price = self.product_id.lst_price
