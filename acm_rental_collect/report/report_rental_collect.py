# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class ReportRentalCollect(models.AbstractModel):
    _name = 'report.acm_rental_collect.report_rental_collection'
    _description = 'Custom Rental Collection Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        Wizard = self.env['rental.collect.report.wizard']
        wizard_id = Wizard.browse(self.env.context.get('active_ids'))
        docs = []
        Result = self.env['rental.collect.report']
        sum = 0.00
        result = Result.search([('group_id', '=', wizard_id.group_id.id)])
        for val in result:
            sum += val.lst_price
            docs.append({
                'product_name': val.product_name,
                'partner_name': val.partner_id.name,
                'type': val.goods_type or '-',
                'price': val.lst_price,
                'amount': '',
            })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_print': wizard_id.date_print,
            'company_name': self.env.user.company_id.name,
            'amount': sum,
            'month': Result.trans_months(wizard_id.date_print.strftime('%m')),
            'docs': docs,
        }
