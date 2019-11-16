# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api
from datetime import datetime
from dateutil.relativedelta import relativedelta


class ReportRentalCollect(models.AbstractModel):
    _name = 'report.acm_rental_collect.report_rental_collection'
    _description = 'Custom Rental Collection Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        Wizard = self.env['rental.collect.report.wizard']
        wizard = Wizard.browse(self.env.context.get('active_ids'))
        products = self.env['product.product'].search(
            [('value_type', '=', 'rent'),
             ('group_id', '=', wizard.group_id.id), ])
        agreement_lines = self.env['agreement.line'].search(
            [('product_id', 'in', products.ids),
             ('agreement_id.state', '=', 'active'),
             ('date_start', '<=', wizard.date_print),
             ('date_end', '>=', wizard.date_print), ])
        line_dict = {}
        sum = 0.00
        for rec in agreement_lines:
            sum += rec.lst_price
            line_dict[rec.product_id.id] = {
                'partner_name': rec.agreement_id.partner_id.display_name,
                'goods_type': rec.product_id.goods_type,
                'lst_price': '%.2f' % rec.lst_price,
            }
        current_date = datetime.today()
        return {
            'year': wizard.date_print.year + 543,
            'month': wizard.trans_months(wizard.date_print.strftime('%m')),
            'end_date': (wizard.date_print + relativedelta(day=31)).day,
            'date_print': wizard.date_print,
            'company_name': self.env.user.company_id.name,
            'current_date': current_date.day,
            'current_month': wizard.trans_months(current_date.strftime('%m')),
            'current_year': current_date.year + 543,
            'amount': sum,
            'line_dict': line_dict,
            'products': products,
        }
