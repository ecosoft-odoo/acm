# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AgreementLine(models.Model):
    _inherit = 'agreement.line'

    @api.multi
    def prepare_contract_line(self):
        return {
            'product_id': self.product_id.id,
            'name': self.name,
            'quantity': self.qty,
            'uom_id': self.uom_id.id,
            'price_unit': self.product_id.lst_price,
        }
