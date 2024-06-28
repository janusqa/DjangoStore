from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    # review the IsAuthenticated class to see how permissions work. We use similar strategy here based on that.
    # 1. Overrid has_permission
    def has_permission(self, request, view):
        # Anyone can retrieve or list.this means HEAD and OPTION request need to auth so we have to be more general
        # if request.method == "GET":
        # Here we make this check more general as not to trap HEAD and OPTION request in needing auth
        # by specifying safe methods, ie. methods that do not mutate data, such as GET, OPTIONS, HEAD
        if request.method in permissions.SAFE_METHODS:
            return True

        # otherwise for any other CRUD method check if user is staff and allow if so otherwise deny by return false evaluation
        return bool(request.user and request.user.is_staff)
