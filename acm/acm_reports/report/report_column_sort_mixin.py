# Copyright 2026 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class ReportColumnSortMixin(models.AbstractModel):
    """ Allow list column header sorting on report columns that SQL can not
    sort. Inherited reports extend _read_group_compute (not read_group) to
    fill in their computed group values. """
    _name = 'report.column.sort.mixin'
    _description = 'Report Column Sort Mixin'

    # ------------------------------------------------------------------
    # Column header sorting
    # ------------------------------------------------------------------
    # Some columns cannot be sorted by SQL and are sorted in Python:
    # - _python_sort_record_fields: non-stored computed columns, on records
    #   (they are also flagged sortable so the list header is clickable)
    # - _python_sort_group_fields: columns whose grouped value is computed
    #   in _read_group_compute (e.g. area deduplicated by lock), on groups
    _python_sort_record_fields = []
    _python_sort_group_fields = []

    @api.model
    def _parse_python_order(self, order, python_fields):
        """ Split ``order`` into (python_parts, sql_order).
        python_parts is the leading run of order parts on ``python_fields``
        as a list of (field, reverse); sql_order is the rest, handled by the
        ORM. Returns ([], order) when the first part is not a python field,
        so the normal ORM ordering is kept. """
        if not order:
            return [], order
        parts = [p.strip() for p in order.split(',') if p.strip()]
        python_parts = []
        for part in parts:
            tokens = part.split()
            if tokens[0] not in python_fields:
                break
            reverse = len(tokens) > 1 and tokens[1].lower() == 'desc'
            python_parts.append((tokens[0], reverse))
        sql_order = ', '.join(parts[len(python_parts):]) or None
        return python_parts, sql_order

    @api.model
    def _python_sort(self, items, python_parts, get_value):
        # Stable sort, applied from the last key to the first one
        items = list(items)
        for fname, reverse in reversed(python_parts):
            items.sort(key=lambda x: get_value(x, fname) or 0.0,
                       reverse=reverse)
        return items

    @api.model
    def _python_sort_record_value(self, rec, fname):
        return rec[fname]

    @api.model
    def _python_sort_group_value(self, line, fname):
        return line.get(fname)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(ReportColumnSortMixin, self).fields_get(
            allfields=allfields, attributes=attributes)
        if not attributes or 'sortable' in attributes:
            for fname in self._python_sort_record_fields:
                if fname in res:
                    res[fname]['sortable'] = True
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        python_parts, sql_order = self._parse_python_order(
            order, self._python_sort_record_fields)
        if not python_parts:
            return super(ReportColumnSortMixin, self).search_read(
                domain=domain, fields=fields, offset=offset, limit=limit,
                order=order)
        records = self.search(domain or [], order=sql_order)
        records = self._python_sort(
            records, python_parts, self._python_sort_record_value)
        start = offset or 0
        records = records[start:start + limit if limit else None]
        if not records:
            return []
        return self.browse([r.id for r in records]).read(fields)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None,
                   orderby=False, lazy=True):
        python_parts, sql_order = self._parse_python_order(
            orderby, self._python_sort_group_fields)
        if not python_parts:
            return self._read_group_compute(
                domain, fields, groupby, offset=offset, limit=limit,
                orderby=orderby, lazy=lazy)
        # Fetch all groups, sort on the final (displayed) values, then page
        res = self._read_group_compute(
            domain, fields, groupby, orderby=sql_order or False, lazy=lazy)
        res = self._python_sort(
            res, python_parts, self._python_sort_group_value)
        start = offset or 0
        return res[start:start + limit if limit else None]

    @api.model
    def _read_group_compute(self, domain, fields, groupby, offset=0,
                            limit=None, orderby=False, lazy=True):
        """ read_group with the computed columns filled in on each group """
        res = super(ReportColumnSortMixin, self).read_group(
            domain, fields, groupby, offset=offset, limit=limit,
            orderby=orderby, lazy=lazy)
        # Without groupby, the single total line has no __domain: add it so
        # the inherited reports compute their values on it too (this gives
        # the list footer totals, see report_list_footer.js)
        if not groupby:
            for line in res:
                line.setdefault('__domain', domain or [])
        return res
