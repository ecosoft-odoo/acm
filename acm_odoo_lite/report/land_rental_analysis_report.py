# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api


class LandRentalAnalysisReport(models.TransientModel):
    _name = "land.rental.analysis.report"
    _description = "Land Rental Analysis Report"

    agreement = fields.Char(
        string="Agreement",
    )
    lessee = fields.Char(
        string="Lessee",
    )
    product = fields.Char(
        string="Product",
    )
    sub_district = fields.Char(
        string="Sub-District",
    )
    district = fields.Char(
        string="District",
    )
    province = fields.Char(
        string="Province",
    )
    land_use = fields.Char(
        string="Land Use",
    )
    land_nla = fields.Float(
        string="Land NLA (SQW)",
        digits=(16, 2),
    )
    land_rented = fields.Float(
        string="Land Rented (SQW)",
        digits=(16, 2),
    )
    percent_of_nla = fields.Float(
        string="% of NLA",
        digits=(16, 2),
    )
    building_rented = fields.Float(
        string="Building Rented (SQM)",
        digits=(16, 2),
    )
    agreement_length = fields.Char(
        string="Agreement Length (Months)",
    )
    monthly_rent_collected_land = fields.Float(
        string="Monthly Rent Collected - Land",
    )
    monthly_rent_collected_building = fields.Float(
        string="Monthly Rent Collected - Land and Building",
    )
    land_monthly_rental_rate = fields.Float(
        string="Land Monthly Rental Rate (THB/SQW/Month)",
    )
    building_monthly_rental_rate = fields.Float(
        string="Land and Building Monthly Rental Rate (THB/SQM/Month)",
    )
    estimated_contractual_rental_revenue = fields.Float(
        string="Estimated Contractual Rental Revenue",
    )
    product_id = fields.Many2one(
        comodel_name="product.template",
        string="Product ID",
    )
    wizard_id = fields.Many2one(
        comodel_name="land.rental.analysis.report.wizard",
        string="Wizard",
        index=True,
    )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        res = super(LandRentalAnalysisReport, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        for line in res:
            if "__domain" in line:
                # Land NLA (SQW)
                report = self.search(line["__domain"])
                product = report.mapped('product_id')
                line["land_nla"] = sum([(p.rai2 * 400) + (p.ngan2 * 100) + p.square_wa2 for p in product])
                # % of NLA
                line["percent_of_nla"] = line["land_rented"] * 100 / (line["land_nla"] or 1)
                # Land Monthly Rental Rate
                line["land_monthly_rental_rate"] = line["monthly_rent_collected_land"] / (sum([r.land_rented for r in report if not r.building_rented]) or 1)
                # Land and Building Monthly Rental Rate
                line["building_monthly_rental_rate"] = line["monthly_rent_collected_building"] / (line["building_rented"] or 1)
                # Agreement Length (Months)
                agreement_length = sum([int(r.agreement_length) for r in report if r.agreement_length]) / (len(report) or 1)
                line["agreement_length"] = "{:,.2f}".format(agreement_length)
        return res


class LandRentalAnalysisReportWizard(models.TransientModel):
    _name = "land.rental.analysis.report.wizard"
    _description = "Land Rental Analysis Report Wizard"

    at_date = fields.Date(
        string="At Date",
        required=True,
        default=fields.Date.context_today,
    ) 
    report_ids = fields.One2many(
        comodel_name="land.rental.analysis.report",
        inverse_name="wizard_id",
        string="Report",
    )

    @api.multi
    def _get_sql(self):
        self.ensure_one()
        sql = """
            select 
                *, sub.land_rented * 100 / coalesce(nullif(sub.land_nla, 0), 1) as percent_of_nla,
                case when sub.building_rented = 0 then sub.estimated_contractual_rental_revenue / coalesce(nullif(sub.agreement_length, 0), 1) else 0 end as monthly_rent_collected_land,
                case when sub.building_rented = 0 then sub.estimated_contractual_rental_revenue / coalesce(nullif(sub.agreement_length, 0), 1) / coalesce(nullif(sub.land_rented, 0), 1) else 0 end as land_monthly_rental_rate,
                case when sub.building_rented <> 0 then sub.estimated_contractual_rental_revenue / coalesce(nullif(sub.agreement_length, 0), 1) else 0 end as monthly_rent_collected_building,
                case when sub.building_rented <> 0 then sub.estimated_contractual_rental_revenue / coalesce(nullif(sub.agreement_length, 0), 1) / coalesce(nullif(sub.building_rented, 0), 1) else 0 end as building_monthly_rental_rate
            from (
                select 
                    a.name as agreement, rp.name as lessee, pt.id as product_id, pt.name as product, pt.sub_district, pt.district, pt.province,
                    gc.name as land_use, (400 * pt.rai2) + (100 * pt.ngan2) + pt.square_wa2 as land_nla,
                    (400 * al.rai) + (100 * al.ngan) + al.square_wa as land_rented,
                    al.square_meter as building_rented, a.installment_number * al.lst_price as estimated_contractual_rental_revenue,
                    (extract(year from age(case when a.termination_date is not null then a.termination_date else a.end_date end + interval '1 day', a.start_date)) * 12 + 
                    extract(month from age(case when a.termination_date is not null then a.termination_date else a.end_date end + interval '1 day', a.start_date))):: integer as agreement_length, {} as wizard_id
                from agreement a
                left join agreement_line al on a.id = al.agreement_id
                left join product_product pp on al.product_id = pp.id
                left join product_template pt on pp.product_tmpl_id = pt.id
                left join res_partner rp on a.partner_id = rp.id
                left join goods_category gc on a.goods_category_id = gc.id
                where a.is_template = False and (a.state = 'active' or (a.state = 'inactive' and a.inactive_reason <> 'cancel')) and 
                    '{}' >= a.start_date and '{}' <= (case when a.termination_date is not null then a.termination_date else a.end_date end) and
                    pt.value_type = 'rent' and pt.active = True
                group by a.id, al.id, pt.id, rp.id, gc.id
            ) sub
        """.format(self.id, self.at_date, self.at_date)
        return sql

    @api.multi
    def view_report(self):
        self.ensure_one()
        # Create Report
        self._cr.execute(self._get_sql())
        res = self._cr.dictfetchall()
        report = self.env["land.rental.analysis.report"].create(res)
        # View Report
        action = self.env.ref("acm_odoo_lite.land_rental_analysis_report_action")
        vals = action.read()[0]
        vals["domain"] = [("wizard_id", "=", self.id)]
        return vals
