# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
import calendar


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
        string='Date',
        required=True,
    )
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        domain=lambda self: self._get_domain_categ_id(),
        required=True,
    )

    @api.model
    def _get_domain_categ_id(self):
        products = self.env['product.template'].search([
            ('value_type', '=', 'rent')])
        categs = products.mapped('categ_id')
        return [('id', 'in', categs.ids)]

    @api.multi
    def print_report(self):
        self.ensure_one()
        datas = {'ids': self.ids, 'model': self._name}
        action = self.env.ref('acm.action_report_rental_collection')
        return action.report_action(self, data=datas)

    @api.model
    def trans_months(self, month):
        months = {
            '01': 'มกราคม',
            '02': 'กุมภาพันธ์',
            '03': 'มีนาคม',
            '04': 'เมษายน',
            '05': 'พฤษภาคม',
            '06': 'มิถุนายน',
            '07': 'กรกฎาคม',
            '08': 'สิงหาคม',
            '09': 'กันยายน',
            '10': 'ตุลาคม',
            '11': 'พฤศจิกายน',
            '12': 'ธันวาคม',
        }
        return months[month]

    @api.multi
    def _get_last_date(self, year, month):
        return calendar.monthrange(year, month)
