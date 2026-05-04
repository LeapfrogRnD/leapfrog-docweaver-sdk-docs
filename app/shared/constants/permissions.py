from app.shared.constants.app_constants import RolesClass

PERMISSIONS: dict[RolesClass, dict[RolesClass, list[str]]] = {
    RolesClass.SUPERADMIN: {
        RolesClass.SUPERADMIN: ["read"],
        RolesClass.ADMIN: ["create", "invite", "update", "delete", "read"],
        RolesClass.USER: ["create", "invite", "update", "delete", "read"],
    },
    RolesClass.ADMIN: {
        RolesClass.SUPERADMIN: [],
        RolesClass.ADMIN: ["read", "update"],
        RolesClass.USER: ["create", "invite", "update", "delete", "read"],
    },
    RolesClass.USER: {
        RolesClass.SUPERADMIN: [],
        RolesClass.ADMIN: [],
        RolesClass.USER: ["read", "update"],
    },
}
