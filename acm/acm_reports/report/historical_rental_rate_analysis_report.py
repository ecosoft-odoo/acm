# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class HistoricalRentalRateAnalysisReport(models.TransientModel):
    _name = 'historical.rental.rate.analysis.report'
    _inherit = 'historical.rental.analysis.report'
    _description = 'Historical Rental Rate Analysis Report'

    agreement_length = fields.Float(
        string='Agreement Length (Months)',
        digits=(16, 2),
    )
    # Calculate Rent Period
    rent_period_net_1 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 1',
    )
    rent_period_net_2 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 2',
    )
    rent_period_net_3 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 3',
    )
    rent_period_net_4 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 3+',
    )
    rent_period_standard_1 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 1',
    )
    rent_period_standard_2 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 2',
    )
    rent_period_standard_3 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 3',
    )
    rent_period_standard_4 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 3+',
    )
    # Calculate Lum Sum Rent
    lump_sum_rent_net = fields.Float(
        compute='_compute_lump_sum_rent',
        string='Lump Sum Rent',
    )
    lump_sum_rent_standard = fields.Float(
        compute='_compute_lump_sum_rent',
        string='Lump Sum Rent',
    )
    # Calculate Average Rental Rate / Sqm / Month
    average_rental_rate_net = fields.Float(
        compute='_compute_average_rental_rate',
        string='Average Rental Rate / Sqm / Month',
    )
    average_rental_rate_standard = fields.Float(
        compute='_compute_average_rental_rate',
        string='Average Rental Rate / Sqm / Month',
    )
    wizard_id = fields.Many2one(
        comodel_name='historical.rental.rate.analysis.report.wizard',
        string='Wizard',
        index=True,
    )

    @api.multi
    def _compute_rent_period(self):
        for rec in self:
            # Filter agreement line for only rent product
            agreement_lines = rec.agreement_id.line_ids.filtered(
                lambda k: k.product_id.value_type == 'rent').sorted(
                    'date_start')
            multiplier, sum_net, sum_standard = 1, 0, 0
            for i, line in enumerate(agreement_lines):
                # Calculate days of period.
                if line.agreement_id.recurring_rule_type == 'daily':
                    multiplier = \
                        (line.date_end + timedelta(1) - line.date_start).days
                elif line.agreement_id.recurring_rule_type == 'monthly':
                    period = relativedelta(line.date_end + timedelta(1), line.date_start)
                    multiplier = period.years * 12 + period.months
                # Calculate Rent Period
                if i <= 2:
                    rec.update({
                        'rent_period_net_%s' % str(i + 1): line.total_price * multiplier,
                        'rent_period_standard_%s' % str(i + 1): line.lst_price * multiplier
                    })
                else:
                    sum_net += line.total_price * multiplier
                    sum_standard += line.lst_price * multiplier
            rec.update({
                'rent_period_net_4': sum_net,
                'rent_period_standard_4': sum_standard,
            })

    @api.multi
    def _compute_lump_sum_rent(self):
        for rec in self:
            agreement_lines = rec.agreement_id.line_ids.filtered(
                lambda k: k.product_id.value_type == 'lump_sum_rent').sorted(
                    'date_start')
            rec.update({
                'lump_sum_rent_net': sum(agreement_lines.mapped('total_price')),
                'lump_sum_rent_standard': sum(agreement_lines.mapped('lst_price')),
            })

    @api.multi
    def _compute_average_rental_rate(self):
        for rec in self:
            total_rent_net, total_rent_standard = 0, 0
            for i in range(4):
                total_rent_net += rec['rent_period_net_%s' % str(i + 1)]
                total_rent_standard += rec['rent_period_standard_%s' % str(i + 1)]
            rec.update({
                'average_rental_rate_net': (total_rent_net + rec['lump_sum_rent_net']) / (rec['occupied_area'] or 1) / (rec['agreement_length'] or 1),
                'average_rental_rate_standard': (total_rent_standard + rec['lump_sum_rent_standard']) / (rec['occupied_area'] or 1) / (rec['agreement_length'] or 1)
            })

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(HistoricalRentalRateAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if '__domain' in line:
                report = self.search(line['__domain'])
                for i in range(4):
                    line.update({
                        'rent_period_net_%s' % str(i + 1): sum(report.mapped('rent_period_net_%s' % str(i + 1))),
                        'rent_period_standard_%s' % str(i + 1): sum(report.mapped('rent_period_standard_%s' % str(i + 1))),
                    })
                line.update({
                    'lump_sum_rent_net': sum(report.mapped('lump_sum_rent_net')),
                    'lump_sum_rent_standard': sum(report.mapped('lump_sum_rent_standard')),
                })
                # Compute Avarage Rental Rate / Sqm / Month
                total_rent_net_per_month, total_rent_standard_per_month = 0.0, 0.0
                for r in report:
                    total_rent_net_per_month += (
                        r.rent_period_net_1 + \
                        r.rent_period_net_2 + \
                        r.rent_period_net_3 + \
                        r.rent_period_net_4 + \
                        r.lump_sum_rent_net) / (r.agreement_length or 1.0)
                    total_rent_standard_per_month += (
                        r.rent_period_standard_1 + \
                        r.rent_period_standard_2 + \
                        r.rent_period_standard_3 + \
                        r.rent_period_standard_4 + \
                        r.lump_sum_rent_standard) / (r.agreement_length or 1.0)
                line.update({
                    'average_rental_rate_net': total_rent_net_per_month / (line['occupied_area'] or 1.0),
                    'average_rental_rate_standard': total_rent_standard_per_month / (line['occupied_area'] or 1.0),
                })
                line.pop('agreement_length')
        return res

    @api.model
    def _get_sql(self):
        res = super(HistoricalRentalRateAnalysisReport, self)._get_sql()
        sql_list = res.split('FROM')
        sql = """
            -- Select column
            %s,
            DATE_PART('year', AGE(a.end_date + 1, a.start_date)) * 12 +
            DATE_PART('month', AGE(a.end_date + 1, a.start_date)) +
            ROUND(CAST(DATE_PART('day', AGE(a.end_date + 1, a.start_date)) / 30 AS NUMERIC), 2) AS
                agreement_length
            -- From table
            FROM %s
        """ % (sql_list[0],
               sql_list[1])
        return sql
