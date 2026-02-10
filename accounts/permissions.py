from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsEmployeeOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: return True
        return request.user.role == 'ADMIN' or obj.user == request.user

class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'ADMIN': return True
        return obj == request.user
