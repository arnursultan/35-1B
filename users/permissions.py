from rest_framework.permissions import BasePermission, SAFE_METHODS

class RolePermissionMixin:
    def user_role(self, request):
        if request.user and request.user.is_authenticated:\
            return request.user.role
        return None

class IsAdminRole(RolePermissionMixin, BasePermission):
    message = "Доступ только для администратора."

    def has_permission(self, request, view):
        return self.get_user_role(request) == "admin"

class IsManageerRole(RolePermissionMixin, BasePermission):
    message = "Доступ только для менеджеров"

    def has_permission(self, request, view):
        return self.get_user_role(request) == "manager"

class IsAdminOrManager(RolePermissionMixin, BasePermission):
    message = "Доступ только для менеджера и администраторов."

    def has_permission(self, request,view):
        return self.get_user_role(request) in ("admin", "manager")

class IsClientRole(RolePermissionMixin, BasePermission):
    message = "Доступ только для клиентов."

    def has_permission(self, request, view):
        return self.get_user_role(request) == "client"

class IsAdminOrManagerOrReadOnly(RolePermissionMixin, BasePermission):
    message = "Изменение доступно только менеджерам и администраторам."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return self.get_user_role(request) in ("admin", "manager")

class IsOwner(BasePermission):
    message = "Вы не являетесь владельцем этого объекта."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsOwnerOrAdmin(BasePermission):
    message = "Доступ запрещён."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.role == "admin":
            return True
        return obj.owner == request.user

class IsOwnerOrReadOnly(BasePermission):
    message = "Изменение доступно только владельцу."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user































