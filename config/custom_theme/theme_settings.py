from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SITE_HEADER": _("CRM"),
    "SITE_TITLE": _("CRM"),
    "SITE_URL": "/admin/",
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Authentication and Authorization"),
                "separator": False,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "person",
                        "link": reverse_lazy("admin:app_users_user_changelist"),
                    },
                    {
                        "title": _("Groups"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        #     {
        #         "title": _("Face ID"),
        #         "separator": True,
        #         "items": [
        #             {
        #                 "title": _("Sessions"),
        #                 "icon": "history",
        #                 "link": reverse_lazy("admin:faceid_facesession_changelist"),
        #             },
        #             {
        #                 "title": _("Events"),
        #                 "icon": "event",
        #                 "link": reverse_lazy("admin:faceid_faceevent_changelist"),
        #             },
        #         ],
        #     },
        #     {
        #         "title": _("Settings"),
        #         "separator": False,
        #         "items": [
        #             {
        #                 "title": _("Camera"),
        #                 "icon": "videocam",
        #                 "link": reverse_lazy("admin:camera_camera_changelist"),
        #             },
        #         ],
        #     },
        ],
    },
}


def environment_callback(request):
    """
    Callback has to return a list of two values represeting text value and the color
    type of the label displayed in top right corner.
    """
    return ["Development", "info"]  # info, danger, warning, success


def badge_callback(request):
    return 3
