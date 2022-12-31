# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api


class HistoricalOccupancyAnalysisReport(models.TransientModel):
    _name = 'historical.occupancy.analysis.report'
    _inherit = 'historical.rental.analysis.report'
    _description = 'Historical Occupancy Analysis Report'

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
    wizard_id = fields.Many2one(
        comodel_name='historical.occupancy.analysis.report.wizard',
        string='Wizard',
        index=True,
    )

    @api.multi
    def _get_expiry_month(self):
        self.ensure_one()
        at_date = datetime.datetime.strptime(
            self._context.get('at_date'), '%d/%m/%Y').date()
        expiry_month = 0
        if self.end_date and self.end_date >= at_date:
            expiry_day = (self.end_date - at_date).days + 1
            if self.start_date > at_date:
                expiry_day = (self.end_date - self.start_date).days + 1
            expiry_month = round(expiry_day / 30, 2)
        return expiry_month

    @api.model
    def _get_expiry_time(self, expiry_month):
        month = int(expiry_month)
        day = (30 / 100 * (expiry_month - month)) * 100
        expiry_time = '{month}M{day}D'.format(month=month, day=day)
        return expiry_time

    @api.multi
    def _compute_expiry_time(self):
        for rec in self:
            expiry_month = rec._get_expiry_month()
            rec.expiry_time = rec._get_expiry_time(expiry_month)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(HistoricalOccupancyAnalysisReport, self).read_group(
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
                expiry_month = sum([r._get_expiry_month() for r in report]) / len(report.filtered(lambda l: l.agreement_id)) / 30
                line['expiry_time'] = self._get_expiry_month(expiry_month)
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
        res = super(HistoricalOccupancyAnalysisReport, self)._get_sql()
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
