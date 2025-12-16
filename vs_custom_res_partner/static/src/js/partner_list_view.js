/** @odoo-module **/
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListRenderer } from "@web/views/list/list_renderer";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

class PartnerDashboardRenderer extends ListRenderer {
    static template = "vs_custom_res_partner.PartnerListView";

    setup() {
        super.setup();
        this.orm = useService("orm");
        this.actionService = useService("action");
        this.actionId = this.env.config.actionId;
        this.dashboardMetrics = useState({ data: {} });

        if (this.props.list?.resModel === "res.partner") {
            onWillStart(async () => {
                try {
                    const data = await this.orm.call("res.partner", "get_dashboard_metrics", [], {});
                    this.dashboardMetrics.data = data;
                    console.warn("[vs_custom_res_partner] Metrics loaded", data);
                } catch (error) {
                    console.warn("Partner dashboard metrics failed", error);
                }
            });
        }
        this.onCardClick = this.onCardClick.bind(this);
    }

    onCardClick(domain, extraContext = {}) {
        const action = {
            type: "ir.actions.act_window",
            name: _t("Customers"),
            res_model: "res.partner",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            view_mode: "list,form",
            target: "current",
            domain,
            context: {
                ...(this.env.searchModel?.context || {}),
                ...extraContext,
            },
        };
        this.actionService.doAction(action, {
            viewType: "list",
        });
    }
}

export const PartnerDashboardListView = {
    ...listView,
    Renderer: PartnerDashboardRenderer,
};

registry.category("views").add("partner_dashboard_list", PartnerDashboardListView);
