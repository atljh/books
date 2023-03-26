from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'book'):
            return obj.book.user == request.user


class IsOwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # if hasattr(obj, 'user'):
        #     return obj.user == request.user
        if hasattr(obj, 'book'):
            rez = obj.book.user == request.user
            return rez


class BuyerReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user in obj.users_with_access.all() or obj.is_free:
                return True
        return False


class Test(permissions.BasePermission):

    # def has_permission(self, request, view):
    #     return False

    def has_object_permission(self, request, view, obj):
        return False


