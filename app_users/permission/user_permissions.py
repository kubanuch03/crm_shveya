

class PermissionUser():

    def __init__(self):
        pass

    def has_change_permission(self, request, obj=None):
        """
        Обычный пользователь может редактировать только свой профиль.
        """
        if obj is None:
            return True  # Разрешаем вход в админку
        return obj.id == request.user.id or request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """
        Обычные пользователи не могут удалять себя или других.
        """
        return request.user.is_superuser