from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static



def custom_user_menu_items(request):
    print("--- DEBUG: Вызвана функция custom_user_menu_items ---") # Добавим вывод в консоль
    items = [
        {
            "title": "ТЕСТ Профиль", # Простой текст без _()
            "link": "/admin/",     # Простая рабочая ссылка (на главную админки)
            "icon": "star",        # Простая иконка
            # Убираем permission для теста
        },
        {
            "title": "ТЕСТ Выход",
            "link": reverse_lazy("admin:logout"), # Оставим, т.к. обычно работает
            "icon": "logout",
        },
    ]
    print(f"--- DEBUG: Возвращаемые элементы: {items} ---") # Выведем результат
    return items



UNFOLD = {
    "SITE_HEADER": _("CRM система"),
    "SITE_TITLE": _("CRM система"),
    "SITE_URL": "/admin/",
    # "SHOW_HISTORY": True,
    "THEME": "dark",
    "BORDER_RADIUS": "6px",
    "USER_MENU_ITEMS": "app_users.views.very_simple_user_menu_items",
    
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Авторизация и Пользователи"),
                "separator": False,
                "permission": lambda request: request.user.is_superuser,
                "items": [
                    {
                        "title": _("Пользователи"),
                        "icon": "person",
                        "link": reverse_lazy("admin:app_users_user_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Группы"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    
                ],
            },

            {
                "title": _("Производтсво"),
                "separator": True,
                "items": [
                    {
                        "title": _("Производственная Партия"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_productions_productionbatch_changelist"),
                    },
                    {
                        "title": _("Товары Входящие в партию"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_productions_batchproduct_changelist"),
                    },
                     {
                        "title": _("Этап производственного процесса"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_productions_processstage_changelist"),
                    },
                     {
                        "title": _("Товар"),
                        "icon": "apparel",
                        "link": reverse_lazy("admin:app_productions_product_changelist"),
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
                            "permission": lambda request: request.user.is_superuser,
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
    
    "DASHBOARD_CALLBACK": "app_accounting.views.dashboard_callback",
    "TABS": [
        {
        
            "items": [
                {
                    "title": ("Your custom title"),
                    "link": reverse_lazy("admin:app_users_user_changelist"),
                    # "permission": "sample_app.permission_callback",
                },
            ],
        },
    ],
}
def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Development", "info"]  # info, danger, warning, success


def badge_callback(request):
    return 3
