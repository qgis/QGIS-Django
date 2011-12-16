import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

# Keep ModelBackend around for per-user permissions and maybe a local superuser.
AUTHENTICATION_BACKENDS = (
  'django_auth_ldap.backend.LDAPBackend',
  'django.contrib.auth.backends.ModelBackend',
  'django.contrib.auth.backends.RemoteUserBackend',
)

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldaps://ldap.osgeo.org"

AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=People,dc=osgeo,dc=org"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
  "first_name": "givenName",
  "last_name": "sn",
  "email": "mail"
}
# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

