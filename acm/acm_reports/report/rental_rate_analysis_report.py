# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta
from odoo import models, fields, api, tools
from dateutil.relativedelta import relativedelta


class RentalRateAnalysisReport(models.Model):
    _name = 'rental.rate.analysis.report'
    _inherit = 'rental.analysis.report'
    _description = 'Rental Rate Analysis Report'
    _auto = False

    agreement_length = fields.Integer(
        string='Agreement Length (Months)',
    )
    # Calculate Rent Period
    rent_period_1 = fields.Float(
        compute='_compute_rent_period',
    )
    rent_period_2 = fields.Float(
        compute='_compute_rent_period',
    )
    rent_period_3 = fields.Float(
        compute='_compute_rent_period',
    )
    rent_period_4 = fields.Float(
        compute='_compute_rent_period',
        string='Rent Period 3+',
    )
    # Calculate Lum Sum Rent
    lump_sum_rent = fields.Float(
        compute='_compute_lump_sum_rent',
    )
    # Calculate Average Rental Rate / Sqm / Month
    average_rental_rate = fields.Float(
        compute='_compute_average_rental_rate',
        string='Average Rental Rate / Sqm / Month',
    )

    @api.multi
    def _compute_rent_period(self):
        for rec in self:
            # Filter agreement line for only rent product
            agreement_lines = rec.agreement_id.line_ids.filtered(
                lambda l: l.product_id.value_type == 'rent').sorted(
                    'date_start')
            multiplier, sum = 1, 0
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
                    rec['rent_period_%s' % str(i+1)] = line.lst_price * multiplier
                else:
                    sum += line.lst_price * multiplier
            rec['rent_period_4'] = sum

    @api.multi
    def _compute_lump_sum_rent(self):
        for rec in self:
            agreement_lines = rec.agreement_id.line_ids.filtered(
                lambda l: l.product_id.value_type == 'lump_sum_rent').sorted(
                    'date_start')
            rec.lump_sum_rent = sum(agreement_lines.mapped('lst_price'))

    @api.multi
    def _compute_average_rental_rate(self):
        for rec in self:
            total_rent = 0
            for i in range(4):
                total_rent += rec['rent_period_%s' % str(i+1)]
            rec.average_rental_rate = \
                (total_rent + rec['lump_sum_rent']) / (rec['area'] or 1) / \
                (rec['agreement_length'] or 1)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RentalRateAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if '__domain' in line:
                report = self.search(line['__domain'])
                for i in range(4):
                    line['rent_period_%s' % str(i+1)] = \
                        sum(report.mapped('rent_period_%s' % str(i+1)))
                line['lump_sum_rent'] = sum(report.mapped('lump_sum_rent'))
                line['average_rental_rate'] = \
                    sum(report.mapped('average_rental_rate')) / len(report)
                line.pop('agreement_length')
        return res

    @api.model
    def _get_sql(self):
        res = super(RentalRateAnalysisReport, self)._get_sql()
        sql_list = res.split('FROM')
        sql = """
            -- Select column
            %s,
            DATE_PART('year', AGE(a.end_date + 1, a.start_date)) * 12 +
            DATE_PART('month', AGE(a.end_date + 1, a.start_date)) AS
                agreement_length
            -- From table
            FROM %s
        """ % (sql_list[0],
               sql_list[1])
        return sql

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)""" % (
            self._table, self._get_sql()))
