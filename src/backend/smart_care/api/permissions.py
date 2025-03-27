from rest_framework import permissions
from api.models import Clients


class IsAdmin(permissions.BasePermission):
    """
    只有管理员角色的用户才有权限访问。
    """
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated and request.user.is_active:
            return request.user.role.role_name == '管理员'
        return False


class IsStaff(permissions.BasePermission):
    """
    只允许员工角色的用户访问。
    """
    def has_permission(self, request, view):
        # 确保用户已登录，并且是员工
        if request.user and request.user.is_authenticated and request.user.is_active:
            return request.user.role.role_name == '员工'
        return False


class IsClient(permissions.BasePermission):
    """
    客户角色的用户访问自身资源
    """
    def has_permission(self, request, view):
        # 确保用户已登录，并且是客户
        if request.user and request.user.is_authenticated and request.user.is_active:
            # 尝试从 URL 路径参数中获取 client_id
            client_id = view.kwargs.get('client_id')

            # 如果路径参数中没有 client_id，则尝试从查询参数中获取
            if client_id is None:
                client_id = int(request.query_params.get('client_id'))
            # 如果两种方式都获取不到 client_id，则拒绝访问
            if client_id is None:
                return False
            return request.user.role.role_name == '客户' and client_id == Clients.objects.get(user_id=request.user.id).client_id
        return False
