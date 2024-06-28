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


# Consider that we want to give permissions to non is_staff to have full/Partial CRUD on an enpont
# depending on the model permissions assinged to a group in the admin ui and then the user assinged to this group.
# Insead of locking this endpoint to IsAdminUser, we can use DjangoModelPermission to allow acces to users that have
# these permissons but is not is_staff, hence no access to admin ui. If we later remove this user from that group, but
# still mantain DjangoModelPermission on that endpoint the user will still have Read access. We may not want that. We may
# want that they have NO access at all.  We will do this by customizing/extendin DjangoModelPermissons to remove SAFE_METHODS, as
# by default if you review DjangoModelPermissions source code you can see that the SAFE_METHODS GET, OPTIONS, HEAD have no permissions
# applied in perms_map, but the other methods do. WE want to change this and apply permssions to the SAFE_METHODS
class StrictDjangoModelPermissions(permissions.DjangoModelPermissions):
    def __init__(self) -> None:
        self.perms_map["GET"] = ["%(app_label)s.view_%(model_name)s"]


# CUSTOM PERMISSION
# implements a customer permission called "view_history" for CustomerViewSet that will be used on the "history"
# action method there.
# so this class returns true if we have assinged this custom permisson to a user in the admin ui.
# So...
# 1. create the custom permission in ViewSet via permissions variable and run migration
# 2. create custom permission class that retuns that returns true for any user who has this permission assigned via admin ui
# 3. assign this permission to users in Admin UI
# 4. apply this permission to the ViewSet via permission_classes OR get_permissions method
class ViewCustomerHistoryPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("store.view_history")
