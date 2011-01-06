from django.conf.urls.defaults import *


urlpatterns = patterns('users.views',

    url("^$", "usersMap", name="show_map"),
    url("^view_users.html$", "usersMap", name="show_map"),
    url("^create_user_form.html$", "createUser", name="create_user"),
    url("^update_user/(?P<theUser>[A-Z,0-9]+) $", "updateUser", name="update_user"),

)
