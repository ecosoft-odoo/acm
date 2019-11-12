# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class RentalCollectReport(models.TransientModel):
    _name = 'rental.collect.report.wizard'
    _description = 'Rental Collection Report'

    date_print = fields.Date(
        default=fields.Date.today,
    )
    agreement_ids = fields.Many2many(
        comodel_name='agreement',
        string='Agreement List',
        default=lambda self: self._context.get('active_ids', []),
    )

    @api.multi
    def print_report(self):
        self.ensure_one()
        datas = {'ids': self.ids, 'model': self._name}
        action = self.env.ref('acm_rental_collect.report_rental_collection')
        return action.report_action(self, data=datas)
