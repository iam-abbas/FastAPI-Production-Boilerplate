from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from core.security.access_control import (
    AccessControl,
    ActionPrincipal,
    Allow,
    Everyone,
    ItemPrincipal,
    RolePrincipal,
    SystemPrincipal,
    UserPrincipal,
)


def test_access_control():
    # Arrange
    ac = AccessControl(user_principals_getter=lambda: [])
    resource = MagicMock()
    resource.__acl__ = lambda: [
        (Allow, Everyone, ["create", "read"]),
        (Allow, SystemPrincipal(value="admin"), ["create", "update", "delete"]),
        (Allow, RolePrincipal(value="editor"), ["update"]),
        (Allow, ItemPrincipal(value="123"), ["read", "update"]),
        (Allow, ActionPrincipal(value="report"), ["read"]),
    ]
    principals = [
        Everyone,
        SystemPrincipal(value="mod"),
        UserPrincipal(value="user1"),
        RolePrincipal(value="editor"),
        ItemPrincipal(value="123"),
        ActionPrincipal(value="report"),
    ]

    # Act and Assert
    assert ac.has_permission(principals, "read", resource) is True
    assert ac.has_permission(principals, "create", resource) is True
    assert ac.has_permission(principals, "update", resource) is True
    assert ac.has_permission(principals, "delete", resource) is False

    assert all(
        permission in ac.show_permissions(principals, resource)
        for permission in ["create", "read", "update"]
    )

    ac.assert_access(principals, "read", resource)
    ac.assert_access(principals, "create", resource)
    ac.assert_access(principals, "update", resource)

    with pytest.raises(HTTPException):
        ac.assert_access(principals, "delete", resource)


def test_access_control_multiple_resources():
    # Arrange
    ac = AccessControl(user_principals_getter=lambda: [])
    resource1 = MagicMock()
    resource1.__acl__ = lambda: [
        (Allow, Everyone, ["create", "read"]),
        (Allow, SystemPrincipal(value="admin"), ["create", "update", "delete"]),
        (Allow, RolePrincipal(value="editor"), ["update"]),
        (Allow, ItemPrincipal(value="123"), ["read", "update"]),
        (Allow, ActionPrincipal(value="report"), ["read"]),
    ]
    resource2 = MagicMock()
    resource2.__acl__ = lambda: [
        (Allow, Everyone, ["read"]),
        (Allow, SystemPrincipal(value="admin"), ["create", "update", "delete"]),
        (Allow, RolePrincipal(value="editor"), ["update"]),
        (Allow, ItemPrincipal(value="123"), ["read", "update"]),
        (Allow, ActionPrincipal(value="report"), ["read"]),
    ]
    principals = [
        Everyone,
        SystemPrincipal(value="mod"),
        UserPrincipal(value="user1"),
        RolePrincipal(value="editor"),
        ItemPrincipal(value="123"),
        ActionPrincipal(value="report"),
    ]

    # Act and Assert
    assert ac.has_permission(principals, "read", [resource1, resource2]) is True
    assert ac.has_permission(principals, "update", [resource1, resource2]) is True
    assert ac.has_permission(principals, "create", [resource1, resource2]) is False
    assert ac.has_permission(principals, "delete", [resource1, resource2]) is False

    assert all(
        permission in ac.show_permissions(principals, [resource1, resource2])
        for permission in ["read", "update"]
    )

    ac.assert_access(principals, "read", [resource1, resource2])
    ac.assert_access(principals, "update", [resource1, resource2])

    with pytest.raises(HTTPException):
        ac.assert_access(principals, "delete", [resource1, resource2])

    with pytest.raises(HTTPException):
        ac.assert_access(principals, "create", [resource1, resource2])
