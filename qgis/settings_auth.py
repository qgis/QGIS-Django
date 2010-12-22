import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType


# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldaps://ldap.osgeo.org"

#AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users,dc=example,dc=com",
#    ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
# or perhaps:
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=People,dc=osgeo,dc=org"

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=People,dc=osgeo,dc=org",
    ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)"
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr="cn")

# Only users in this group can log in.

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

#AUTH_LDAP_PROFILE_ATTR_MAP = {
#    "uid": "uid"
#}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
# TODO: only if we figure out the next section
AUTH_LDAP_FIND_GROUP_PERMS = True

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    "is_active": "cn=active,ou=django,ou=groups,dc=example,dc=com",
#    "is_staff": "cn=staff,ou=django,ou=groups,dc=example,dc=com",
#Major guess
    "is_superuser": "cn=admin,ou=projects,ou=qgis,ou=groups,dc=osgeo,dc=org"
}

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600


# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)


















