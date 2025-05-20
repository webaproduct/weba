{
    "name": "oleg_weba_weba17",
    "summary": """
        """,
    "author": "Oleg (Weba)",
    "website": "https://weba.com.ua/",
    "category": "Uncategorized",
    "license": "LGPL-3",
    "version": "17.0.4.0.0",
    "depends": ["account", "project", "crm", "hr_timesheet",
                "sms"],
    "data": [
        "security/ir.model.access.csv",

        "data/ir_sequence_account_move_data.xml",

        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/agreement_views.xml",
        "views/crm_lead_views.xml",
        "views/project_project_views.xml",
        "views/project_month_views.xml",
    ],
}
