import functools
from dataclasses import dataclass
from typing import Any, List

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

Allow: str = "allow"
Deny: str = "deny"


@dataclass(frozen=True)
class Principal:
    key: str
    value: str

    def __repr__(self) -> str:
        return f"{self.key}:{self.value}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass(frozen=True)
class SystemPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="system", value=value, *args, **kwargs)


@dataclass(frozen=True)
class UserPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="user", value=value, *args, **kwargs)


@dataclass(frozen=True)
class RolePrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="role", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ItemPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="item", value=value, *args, **kwargs)


@dataclass(frozen=True)
class ActionPrincipal(Principal):
    def __init__(self, value: str, *args, **kwargs) -> None:
        super().__init__(key="action", value=value, *args, **kwargs)


Everyone = SystemPrincipal(value="everyone")
Authenticated = SystemPrincipal(value="authenticated")


class AllowAll:
    def __contains__(self, item: Any) -> bool:
        return True

    def __repr__(self) -> str:
        return "*"

    def __str__(self) -> str:
        return self.__repr__()


default_exception = HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Forbidden")


class AccessControl:
    def __init__(
        self,
        user_principals_getter: Any,
        permission_exception: Any = default_exception,
    ) -> None:
        self.user_principals_getter = user_principals_getter
        self.permission_exception = permission_exception

    def __call__(self, permissions: str):
        def _permission_dependency():
            enforce = functools.partial(self._enforce, permissions)
            return enforce

        return _permission_dependency

    def _enforce(self, permissions: str, resource: Any):
        if not isinstance(resource, list):
            resource = [resource]

        granted = True
        principals = self.user_principals_getter()

        for resource_obj in resource:
            if not self.has_permission(
                principals=principals,
                required_permissions=permissions,
                resource=resource_obj,
            ):
                granted = False
                break

        if not granted:
            raise self.permission_exception

    def return_allowed(self, permissions: str, resource: Any):
        if not isinstance(resource, list):
            resource = [resource]

        allowed_resources = []
        principals = self.user_principals_getter()

        for resource_obj in resource:
            if self.has_permission(
                principals=principals,
                required_permissions=permissions,
                resource=resource_obj,
            ):
                allowed_resources.append(resource)

        return allowed_resources

    def has_permission(
        self, principals: List[Principal], required_permissions: str, resource: Any
    ):
        acl = self._acl(resource)
        if not isinstance(required_permissions, list):
            required_permissions = [required_permissions]

        for action, principal, permission in acl:
            is_required_permissions_in_permission = all(
                required_permission in permission
                for required_permission in required_permissions
            )
            if (action == Allow and is_required_permissions_in_permission) and (
                principal in principals or principal == Everyone
            ):
                return True

        return False

    def show_permissions(self, principals: List[Principal], resource: Any):
        acl = self._acl(resource)
        permissions = []
        for action, principal, permission in acl:
            if action == Allow and principal in principals or principal == Everyone:
                permissions.append(permission)

        permissions = list(set(self._flatten(permissions)))
        return permissions

    def _acl(self, resource):
        acl = getattr(resource, "__acl__", [])
        if callable(acl):
            return acl()
        return acl

    def _flatten(self, any_list: List[Any]) -> List[Any]:
        flat_list = []
        for element in any_list:
            if isinstance(element, list):
                flat_list += self._flatten(element)
            else:
                flat_list.append(element)
        return flat_list
