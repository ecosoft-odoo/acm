# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class HistoricalRentalRateAnalysisReportWizard(models.TransientModel):
    _name = 'historical.rental.rate.analysis.report.wizard'
    _description = 'Historical Rental Rate Analysis Report Wizard'

    at_date = fields.Date(
        string='At Date',
        required=True,
        default=fields.Date.context_today,
    )
    report_ids = fields.One2many(
        comodel_name='historical.rental.rate.analysis.report',
        inverse_name='wizard_id',
        string='Report',
    )

    @api.multi
    def view_report(self):
        self.ensure_one()
        context = self._context.copy()
        if context is None:
            context = {}
        context['at_date'] = self.at_date
        # Create Report
        Report = self.env['historical.rental.rate.analysis.report']
        sql = Report.with_context(context)._get_sql()
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        report = Report.create(res)
        report.write({'wizard_id': self.id})
        # View Report
        action = self.env.ref('acm.historical_rental_rate_analysis_report_action')
        vals = action.read()[0]
        if context.get('is_net_price'):
            vals['name'] = 'Rental Rate Analysis - Net Price'
        if context.get('is_standard_price'):
            vals['name'] = 'Rental Rate Analysis - Standard Price'
        vals['display_name'] = vals['name']
        vals['domain'] = [('wizard_id', '=', self.id)]
        vals['context'] = {'at_date': self.at_date.strftime('%d/%m/%Y')}
        return vals
