# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class RentalAnalysisReport(models.AbstractModel):
    _name = 'rental.analysis.report'
    _description = 'Rental Analysis Report'

    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
        string='Zone',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product',
    )
    attribute_value_ids = fields.Many2many(
        comodel_name='product.attribute.value',
        string='Attribute Values',
        related='product_id.attribute_value_ids',
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
    )
    occupied_area = fields.Float(
        string='Area Occupied',
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
                # Area For Lease
                self._cr.execute("""
                    SELECT product_tmpl_id, area
                    FROM "{}"
                    WHERE id IN %s
                    GROUP BY product_tmpl_id, area""".format(self._table), (
                        tuple(report.ids), ))
                line['area'] = sum(map(
                    lambda l: l['area'], self._cr.dictfetchall()))
                # Area Occupied
                self._cr.execute("""
                    SELECT product_tmpl_id, area
                    FROM "{}"
                    WHERE id IN %s AND agreement_id IS NOT NULL AND
                    NOW() >= start_date AND NOW() <= end_date
                    GROUP BY product_tmpl_id, area""".format(self._table), (
                        tuple(report.ids), ))
                line['occupied_area'] = sum(map(
                    lambda l: l['area'], self._cr.dictfetchall()))
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
            CASE WHEN a.id IS NOT NULL AND NOW() >= a.start_date AND
            NOW() <= a.end_date AND pt.area IS NOT NULL THEN pt.area
            ELSE %s END""" % (else_value, )
        return select

    @api.model
    def _get_sql(self):
        sql = """
            SELECT ROW_NUMBER() OVER(ORDER BY pp.id, a.id) AS id,
                   pt.group_id, pp.id AS product_id, a.partner_id,
                   a.id AS agreement_id, pp.goods_category_id, a.start_date,
                   a.end_date, %s AS area, %s AS occupied_area, pt.value_type,
                   pp.product_tmpl_id
            FROM product_product pp
            LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
            LEFT JOIN agreement a ON pp.id = a.rent_product_id AND
            a.state = 'active'
            WHERE pt.value_type = 'rent' AND pp.active IS TRUE
        """ % (self._get_sql_area_select(),
               self._get_sql_area_occupied_select())
        return sql
