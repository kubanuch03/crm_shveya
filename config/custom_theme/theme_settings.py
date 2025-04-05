from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_HEADER": _("CRM система"),
    "SITE_TITLE": _("CRM система"),
    "SITE_URL": "/admin/",
    "SHOW_HISTORY": True,
    "THEME": "dark",
    "SHOW_HISTORY": True,
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Авторизация и Пользователи"),
                "separator": False,
                "items": [
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:app_users_user_changelist"),
                    },
                    {
                        "title": _("Группы"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
    
            {
                "title": _("Товар"),
                "separator": True,
                "items": [
                    {
                        "title": _("Процесс Карго"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_logistics_logistics_changelist"),
                    },
                    {
                        "title": _("Товар"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_productions_product_changelist"),
                    },
                     {
                        "title": _("Процесс Упаковки"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_packaging_productprocess_changelist"),
                    },
                     {
                        "title": _("Процесс Утюг"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_utug_utugprocess_changelist"),
                    },
                    {
                        "title": _("Процесс Шитья"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_tailor_tailorprocess_changelist"),
                    },
                    {
                        "title": _("Процесс Кроя"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_croi_croi_changelist"),
                    },
                    
                    ],
                    
                   

            },
           
            {
                 "title": _("Логи"),
                    "separator": True,
                    "items": [
                        {
                            "title": _("История"),
                            "icon": "history",
                            "link": reverse_lazy("admin:app_history_adminhistorylog_changelist"),
                        },
                    ]
            },
            # {
            #     "title": _("Моделю"),
            #     "separator": False,
            #     "items": [
            #         {
            #             "title": _("Модель товара"),
            #             "icon": "videocam",
            #             "link": reverse_lazy("admin:camera_camera_changelist"),
            #         },
            #     ],
            # },
        ],
    },
    
    "DASHBOARD_CALLBACK": "app_users.views.dashboard_callback",

}


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Development", "info"]  # info, danger, warning, success


def badge_callback(request):
    return 3

