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
        agreement_lines = self.env['agreement.line'].search(
            [
                ('agreement_id.state', '=', 'active'),
                ('agreement_id.recurring_rule_type', '=', wizard.recurring_rule_type),
                ('product_id.value_type', '=', 'rent'),
                ('product_id.group_id', '=', wizard.group_id.id),
                ('date_start', '<=', wizard.date_print),
                ('date_end', '>=', wizard.date_print),
            ])
        products = agreement_lines.mapped('product_id').sorted(
            lambda k: (k.group_id, k.lock_number))
        line_dict = {}
        for rec in agreement_lines:
            line_dict[rec.product_id.id] = {
                'partner_name': rec.agreement_id.partner_id.display_name,
                'total_price': '%.2f' % rec.total_price,
            }
        amount = sum([float(x['total_price']) for x in list(line_dict.values())])
        return {
            'current_date': datetime.today(),
            'amount': amount,
            'line_dict': line_dict,
            'products': products,
            'wizard': wizard,
        }
