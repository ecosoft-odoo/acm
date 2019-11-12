# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api
from dateutil.relativedelta import relativedelta


class ReportRentalCollect(models.AbstractModel):
    _name = 'report.acm_rental_collect.report_rental_collection'
    _description = 'Custom Rental Collection Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        Wizard = self.env['rental.collect.report.wizard']
        wizard_id = Wizard.browse(self.env.context.get('active_ids'))
        agreement_ids = wizard_id.agreement_ids
        last_day = (wizard_id.date_print + relativedelta(day=31)).day
        docs = []
        for agreement in agreement_ids:
            docs.append({
                'lock': agreement.rent_product_id.name,
                'partner': agreement.partner_id.name,
                'type': agreement.rent_product_id.goods_type or '-',
                'price': agreement.line_ids.lst_price,
            })
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'print_date': wizard_id.date_print,
            'last_day': last_day,
            'company_name': self.env.user.company_id.name,
            'docs': docs,
        }
