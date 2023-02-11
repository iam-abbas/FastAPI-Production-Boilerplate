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

    def __call__(self, permission: str):
        def _permission_dependency():
            enforce = functools.partial(self.enforce, permission)
            return enforce

        return _permission_dependency

    def enforce(self, permission: str, resource: Any):
        if not self.has_permission(
            principals=self.user_principals_getter(),
            required_permission=permission,
            resource=resource,
        ):
            raise self.permission_exception

    def has_permission(
        self, principals: List[Principal], required_permission: str, resource: Any
    ):
        acl = self._acl(resource)

        for action, principal, permission in acl:
            if (action == Allow and required_permission in permission) and (
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
