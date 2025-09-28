from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на чтение всем, на изменение только владельцу записи.
    """

    def has_object_permission(self, request, view, obj):
        # Разрешить чтение всем запросам
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение только владельцу
        return obj.owner == request.user
