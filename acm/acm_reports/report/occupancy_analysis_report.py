# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

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
    occupancy = fields.Float(
        string='Occupancy',
    )
    total_occupancy = fields.Float(
        string='Contribution to Total Occupancy',
    )

    @api.multi
    def _get_expiry_day(self):
        self.ensure_one()
        now = fields.Date.context_today(self)
        expiry_day = 0
        if self.end_date and self.end_date >= now:
            expiry_day = (self.end_date - now).days + 1
            if self.start_date > now:
                expiry_day = (self.end_date - self.start_date).days + 1
        return expiry_day

    @api.model
    def _get_expiry_time(self, expiry_month):
        month = int(expiry_month)
        day = int(round(30 * (expiry_month - month), 0))
        expiry_time = '{month}M{day}D'.format(month=month, day=day)
        return expiry_time

    @api.multi
    def _compute_expiry_time(self):
        for rec in self:
            expiry_day = rec._get_expiry_day()
            expiry_month = round(expiry_day / 30, 2)
            rec.expiry_time = rec._get_expiry_time(expiry_month)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(OccupancyAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        # Find total area
        report = self.env['occupancy.analysis.report']
        for line in res:
            if '__domain' in line:
                report |= self.search(line['__domain'])
        self._cr.execute("""
            SELECT MAX(area)
            FROM {}
            WHERE id IN %s
            GROUP BY group_id, lock_number""".format(self._table), (tuple(report.ids), ))
        total_area = sum(list(filter(lambda x: x, map(lambda k: k[0], self._cr.fetchall()))))
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
                expiry_day = sum([r._get_expiry_day() for r in report])
                expiry_month = round(expiry_day / (len(report.filtered(lambda k: k.agreement_id)) or 1) / 30, 2)
                line['expiry_time'] = self._get_expiry_time(expiry_month)
        return res

    @api.model
    def _get_sql(self):
        res = super(OccupancyAnalysisReport, self)._get_sql()
        # Find total area
        self._cr.execute("""
            SELECT SUM(area)
            FROM (
                SELECT MAX(r.area) AS area
                FROM ({}) AS r
                GROUP BY r.group_id, r.lock_number
            ) AS x""".format(res))
        total_area = sum(list(filter(lambda x: x, map(lambda k: k[0], self._cr.fetchall()))))
        # --
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
               total_area or 1,
               sql_list[1])
        return sql

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""CREATE OR REPLACE VIEW %s AS (%s)""" % (
            self._table, self._get_sql()))
