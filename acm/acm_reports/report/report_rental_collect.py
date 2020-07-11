# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api
from datetime import datetime


class ReportRentalCollect(models.AbstractModel):
    _name = 'report.acm.report_rental_collection'
    _description = 'Custom Rental Collection Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        Wizard = self.env['rental.collect.report.wizard']
        wizard = Wizard.browse(self.env.context.get('active_ids'))
        products = self.env['product.product'].search(
            [('value_type', '=', 'rent'),
             ('categ_id', '=', wizard.categ_id.id),
             ('group_id', '=', wizard.group_id.id), ])
        agreement_lines = self.env['agreement.line'].search(
            [('product_id', 'in', products.ids),
             ('agreement_id.state', '=', 'active'),
             ('date_start', '<=', wizard.date_print),
             ('date_end', '>=', wizard.date_print), ])
        line_dict = {}
        for rec in agreement_lines:
            line_dict[rec.product_id.id] = {
                'partner_name': rec.agreement_id.partner_id.display_name,
                'goods_type': rec.product_id.goods_type,
                'lst_price': '%.2f' % rec.lst_price,
            }
        amount = sum([float(x['lst_price']) for x in list(line_dict.values())])
        return {
            'current_date': datetime.today(),
            'amount': amount,
            'line_dict': line_dict,
            'products': products,
            'wizard': wizard,
        }
