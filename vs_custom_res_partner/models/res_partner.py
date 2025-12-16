from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    activity_bell_html = fields.Html(
        compute="_compute_activity_bell_html",
        sanitize=False,
        store=False,
    )
    invoice_overdue = fields.Boolean(
        compute="_compute_invoice_overdue",
        store=False,
    )

    @api.depends("activity_state")
    def _compute_activity_bell_html(self):
        for partner in self:
            color = "text-danger" if partner.activity_state == "overdue" else "text-muted"
            partner.activity_bell_html = f"<i class=\"fa fa-bell {color}\"></i>"

    @api.model
    def get_dashboard_metrics(self):
        """Return counts for dashboard cards."""
        if not self.env.user.has_group("base.group_user"):
            return {}
        total_customers = self.with_context(active_test=False).search_count([])
        active_customers = self.search_count([("active", "=", True)])
        warning_customers = self.search_count([("message_needaction", "=", True)])
        total_areas = 0  # placeholder until real field/logic is provided
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "warning_customers": warning_customers,
            "total_areas": total_areas,
        }

    def _compute_invoice_overdue(self):
        """Flag partners that have overdue customer invoices."""
        if not self:
            return
        commercial_ids = self.commercial_partner_id.ids
        move_model = self.env["account.move"]
        # Group overdue invoices by commercial partner
        data = move_model.read_group(
            domain=[
                ("commercial_partner_id", "in", commercial_ids),
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("payment_state", "in", ["not_paid", "partial"]),
                ("invoice_date_due", "<", fields.Date.today()),
                ("state", "=", "posted"),
            ],
            fields=["commercial_partner_id"],
            groupby=["commercial_partner_id"],
        )
        overdue_partner_ids = {rec["commercial_partner_id"][0] for rec in data if rec["commercial_partner_id"]}
        for partner in self:
            partner.invoice_overdue = partner.commercial_partner_id.id in overdue_partner_ids
