from rest_framework.permissions import BasePermission


class IsCustomer(BasePermission):
    """
    Custom permission to only allow customers to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role == 2


class IsDeliveryAgent(BasePermission):
    """
    Custom permission to only allow delivery agents to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role == 3


class IsDeliveryAgentOrAdmin(BasePermission):
    """
    Custom permission to only allow delivery agents or admin to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role in {1, 3}
