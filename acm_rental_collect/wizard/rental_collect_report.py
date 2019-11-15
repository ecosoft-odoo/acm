# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class RentalCollectReport(models.TransientModel):
    _name = 'rental.collect.report.wizard'
    _description = 'Rental Collection Report'

<<<<<<< HEAD
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
        required=True,
=======
    date_print = fields.Date(
        default=fields.Date.today,
    )
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
>>>>>>> 52bfeeaa6666b18b28b378a4398267587a32f1d5
    )
    date_print = fields.Date()

    @api.multi
    def print_report(self):
        self.ensure_one()
        # Get Result Report
        Result = self.env['rental.collect.report']
<<<<<<< HEAD
        result = Result.search([('group_id', '=', self.group_id.id)])
        # docs = []
        # for val in result:
        #     docs.append({
        #         'product_name': val.product_name,
        #         'partner': val.partner_id.name or '',
        #         'type': val.goods_type or '',
        #         'price': val.lst_price,
        #     })
        # Get PDF Report
        report_name = 'acm_rental_collect.report_rental_collection'
        return {
            'doc_ids': result.ids,
            'doc_model': result._name,
            'type': 'ir.actions.report',
            'report_name': report_name,
            'report_type': 'qweb-pdf',
            'docs': result,
=======
        result = Result.search([('product_tmpl_id.group_id', '=', self.group_id.id)])
        # Get PDF Report
        report_name = 'acm_rental_collect.report_rental_collection'
        for x in result:
            x=5/0
        return {
            'type': 'ir.actions.report',
            'report_name': report_name,
            'datas': {'ids': result.ids, 'model': result._name, },
>>>>>>> 52bfeeaa6666b18b28b378a4398267587a32f1d5
        }
