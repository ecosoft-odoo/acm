from odoo import tools
from odoo import models, fields


class RentalCollectReport(models.Model):
    _name = 'rental.collect.report'
    _description = 'Rental Collect Report'
    _auto = False
    _order = 'lock_number'

    product_id = fields.Many2one(
        comodel_name='product.product',
    )
    lock_number = fields.Char()
    name = fields.Char()
    list_price = fields.Float()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE or REPLACE VIEW rental_collect_report as (
                select
                    pt.id, pt.lock_number, pt.name, pt.list_price
                    from product_template pt left join agreement_line agl
                    on agl.product_id = pt.id
            )
        """)
