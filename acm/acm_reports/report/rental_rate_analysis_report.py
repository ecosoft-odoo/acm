# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta
from odoo import models, fields, api, tools


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

    @api.multi
    def _compute_rent_period(self):
        for rec in self:
            # Filter agreement line for only rent product
            agreement_lines = rec.agreement_id.line_ids.filtered(
                lambda l: l.product_id.value_type == 'rent').sorted(
                    'date_start')
            days, sum = 1, 0
            for i, line in enumerate(agreement_lines):
                # Calculate days of period.
                if line.agreement_id.recurring_rule_type == 'daily':
                    days = \
                        (line.date_end + timedelta(1) - line.date_start).days
                # Calculate Rent Period
                if i <= 2:
                    rec['rent_period_%s' % str(i+1)] = line.lst_price * days
                else:
                    sum += line.lst_price * days
            rec['rent_period_4'] = sum

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
