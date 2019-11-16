# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class RentalCollectReport(models.TransientModel):
    _name = 'rental.collect.report.wizard'
    _description = 'Rental Collection Report'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        required=True,
    )
    date_print = fields.Date(
        default=fields.Date.today,
        readonly=True,
    )
    date_range_id = fields.Many2one(
        comodel_name='date.range',
        string='Date Range',
        required=True,
    )

    @api.multi
    def print_report(self):
        self.ensure_one()
        Result = self.env['rental.collect.report']
        result = Result.search([('group_id', '=', self.group_id.id)])
        datas = {'ids': result.ids, 'model': result._name}
        action = self.env.ref(
            'acm_rental_collect.action_report_rental_collection')
        return action.report_action(self, data=datas)
