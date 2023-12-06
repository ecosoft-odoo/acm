# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


class RentalAnalysisReport(models.AbstractModel):
    _name = 'rental.analysis.report'
    _description = 'Rental Analysis Report'
    _order = 'group_id, lock_number, subzone'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
    )
    subzone = fields.Char(
        string='Subzone',
    )
    lock_number = fields.Char(
        string='Lock Number',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Lessee',
    )
    agreement_id = fields.Many2one(
        comodel_name='agreement',
        string='Agreement',
    )
    goods_category_id = fields.Many2one(
        comodel_name='goods.category',
        string='Goods Category',
    )
    start_date = fields.Date(
        string='Start Date',
    )
    end_date = fields.Date(
        string='End Date',
    )
    area = fields.Float(
        string='Area For Lease',
        digits=dp.get_precision('Area'),
    )
    occupied_area = fields.Float(
        string='Area Occupied',
        digits=dp.get_precision('Area'),
    )
    value_type = fields.Selection(
        selection=[
            ('rent', 'Rent'),
            ('lump_sum_rent', 'Lump Sum Rent'),
            ('security_deposit', 'Security Deposit'),
            ('transfer', 'Transfer'), ],
        string='Value Type',
    )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(RentalAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if '__domain' in line:
                report = self.search(line['__domain'])
                # Area For Lease, Area Occupied
                self._cr.execute("""
                    SELECT MAX(area), MAX(occupied_area)
                    FROM {}
                    WHERE id IN %s
                    GROUP BY group_id, lock_number""".format(self._table), (tuple(report.ids), ))
                result = self._cr.fetchall()
                line.update({
                    'area': sum(list(filter(lambda x: x, map(lambda k: k[0], result)))),
                    'occupied_area': sum(list(filter(lambda x: x, map(lambda k: k[1], result)))),
                })
        return res

    @api.model
    def _get_sql_area_select(self, else_value=0):
        select = """
            CASE WHEN pt.area IS NOT NULL AND pt.area <> 0
            THEN pt.area ELSE %s END
        """ % (else_value, )
        return select

    @api.model
    def _get_sql_area_occupied_select(self, else_value=0):
        select = """
            CASE WHEN a.id IS NOT NULL AND pt.area IS NOT NULL AND pt.area <> 0
            THEN pt.area ELSE %s END
        """ % (else_value, )
        return select

    @api.model
    def _get_sql(self):
        sql = """
            SELECT ROW_NUMBER() OVER(ORDER BY pp.id, a.id) AS id,
                   pt.group_id, pt.subzone, pt.lock_number, pp.id AS product_id, a.partner_id,
                   a.id AS agreement_id, a.goods_category_id, a.start_date,
                   a.end_date, %(area_select)s AS area, %(area_occupied_select)s AS occupied_area, pt.value_type
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN (
                SELECT rent_product_id, MAX(id) AS id
                FROM agreement
                WHERE state != 'draft' AND active_date IS NOT NULL AND %(at_date)s BETWEEN start_date AND
                (CASE
                    WHEN termination_date IS NOT NULL THEN termination_date
                    ELSE end_date
                END)
                GROUP BY rent_product_id
            ) AS a_sub ON pp.id = a_sub.rent_product_id
            LEFT JOIN agreement a ON a_sub.id = a.id
            WHERE pt.value_type = 'rent' AND pt.date_start IS NOT NULL AND %(at_date)s >= pt.date_start AND
            (pt.date_end IS NULL OR (pt.date_end IS NOT NULL AND %(at_date)s <= pt.date_end))
        """
        sql = sql % {
            'area_select': self._get_sql_area_select(),
            'area_occupied_select': self._get_sql_area_occupied_select(),
            'at_date': "DATE(NOW() + INTERVAL '7 HOUR')"
        }
        return sql
