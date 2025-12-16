{
    "name": "VS Custom Res Partner Dashboard",
    "version": "1.0",
    "summary": "Adds dashboard cards and activity bell to partners list view",
    "author": "Custom Development",
    "license": "LGPL-3",
    "depends": ["base", "contacts", "web"],
    "data": [
        "views/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "vs_custom_res_partner/static/src/js/partner_list_view.js",
            "vs_custom_res_partner/static/src/xml/partner_dashboard.xml",
            "vs_custom_res_partner/static/src/scss/partner_dashboard.scss",
        ],
    },
    "installable": True,
    "application": False,
}
