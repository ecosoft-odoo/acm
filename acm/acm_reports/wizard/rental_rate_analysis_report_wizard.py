# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class RentalRateAnalysisReportWizard(models.TransientModel):
    _name = 'rental.rate.analysis.report.wizard'
    _description = 'Rental Rate Analysis Report Wizard'

    at_date = fields.Date(
        string='At Date',
        required=True,
        default=fields.Date.today(),
    )

    @api.multi
    def view_report(self):
        self.ensure_one()
        context = self._context.copy()
        if context is None:
            context = {}
        context['at_date'] = self.at_date
        # Create Report
        Report = self.env['rental.rate.analysis.report']
        sql = Report.with_context(context)._get_sql()
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        report = Report.create(res)
        report.write({'wizard_id': self.id})
        # View Report
        action = self.env.ref('acm.rental_rate_analysis_report_action')
        vals = action.read()[0]
        vals['domain'] = [('wizard_id', '=', self.id)]
        return vals