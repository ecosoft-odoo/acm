# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools


class OccupancyAnalysisReport(models.Model):
    _name = 'occupancy.analysis.report'
    _inherit = 'rental.analysis.report'
    _description = 'Occupancy Analysis Report'
    _auto = False

    expiry_time = fields.Char(
        string='Time to Expiry (Months)',
        compute='_compute_expiry_time',
    )
    expiry_day = fields.Integer(
        string='Time to Expiry (Days)',
        compute='_compute_expiry_day',
    )
    occupancy = fields.Float(
        string='Occupancy',
    )
    total_occupancy = fields.Float(
        string='Contribution to Total Occupancy',
    )

    @api.multi
    def _compute_expiry_time(self):
        now = fields.Date.context_today(self)
        for rec in self:
            expiry_time = '00M.00D'
            if rec.end_date and rec.end_date >= now:
                time = relativedelta(rec.end_date, now)
                if rec.start_date > now:
                    time = relativedelta(
                        rec.end_date, rec.start_date - timedelta(1))
                expiry_time = '%sM.%sD' % (
                    str(time.years * 12 + time.months).zfill(2),
                    str(time.days).zfill(2))
            if not rec.agreement_id:
                expiry_time = ''
            rec.expiry_time = expiry_time

    @api.multi
    def _compute_expiry_day(self):
        now = fields.Date.context_today(self)
        for rec in self:
            expiry_day = 0
            if rec.end_date and rec.end_date >= now:
                expiry_day = (rec.end_date - now).days
                if rec.start_date > now:
                    expiry_day = (rec.end_date - (rec.start_date - timedelta(1))).days
            rec.expiry_day = expiry_day

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(OccupancyAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        # Find total area
        Product = self.env['product.template']
        product = Product.search([('value_type', '=', 'rent')])
        total_area = sum(product.mapped('area'))
        # --
        for line in res:
            if '__domain' in line:
                report = self.search(line['__domain'])
                # Occupancy
                line['occupancy'] = \
                    (line['occupied_area'] / (line['area'] or 1)) * 100
                # Contribution to Total Occupancy
                line['total_occupancy'] = \
                    (line['occupied_area'] / (total_area or 1)) * 100
                # Time to Expiry (Months)
                line['expiry_time'] = '%sM' % '{:,.2f}'.format(sum(report.mapped('expiry_day')) / len(report) / 30)
        return res

    @api.model
    def _get_sql_total_area_select(self):
        select = """
            SELECT SUM(area)
            FROM product_template WHERE value_type = 'rent'
        """
        return select

    @api.model
    def _get_sql(self):
        res = super(OccupancyAnalysisReport, self)._get_sql()
        sql_list = res.split('FROM')
        sql = """
            -- Select column
            %s,
            -- Occupancy
            ((%s) / (%s)) * 100 AS occupancy,
            -- Total Occupancy
            ((%s) / (%s)) * 100 AS total_occupancy
            -- From table
            FROM %s
        """ % (sql_list[0],
               self._get_sql_area_occupied_select(),
               self._get_sql_area_select(else_value=1),
               self._get_sql_area_occupied_select(),
               self._get_sql_total_area_select(),
               sql_list[1])
        return sql

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)""" % (
            self._table, self._get_sql()))
