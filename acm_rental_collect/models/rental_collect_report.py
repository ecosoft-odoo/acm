from odoo import tools
from odoo import models, fields, api


class RentalCollectReport(models.Model):
    _name = 'rental.collect.report'
    _description = 'Rental Collect Report'
    _auto = False

    product_name = fields.Char()
    group_id = fields.Many2one(
        comodel_name='account.analytic.group',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
    )
    goods_type = fields.Char()
    lst_price = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW rental_collect_report as (
                select
                    row_number() over(
                        order by pt.group_id, cast(lock_number as int)) as id,
                    pt.group_id,
                    pt.name as product_name,
                    ag.partner_id,
                    pt.goods_type,
                    agl.lst_price,
                    agl.date_start,
                    agl.date_end
                from
                    product_template pt
                    left join product_product pp on pt.id = pp.product_tmpl_id
                    left join agreement_line agl on pp.id = agl.product_id
                    left join agreement ag on agl.agreement_id = ag.id
                    where pt.value_type = 'rent'
                    order by pt.group_id, cast(lock_number as int)
            )
        """)

    @api.model
    def trans_months(self, month):
        months = {
            '01': 'มกราคม',
            '02': 'กุมภาพันธ์',
            '03': 'มีนาคม',
            '04': 'เมษายน',
            '05': 'พฤษภาคม',
            '06': 'มิถุนายน',
            '07': 'กรกฎาคม',
            '08': 'สิงหาคม',
            '09': 'กันยายน',
            '10': 'ตุลาคม',
            '11': 'พฤศจิกายน',
            '12': 'ธันวาคม',
        }
        return months[month]
