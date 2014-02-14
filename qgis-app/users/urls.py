from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView


urlpatterns = patterns('users.views',
    url("^$", "usersMap", name="show_map"),
    url("^view_users.html$", "usersMap", name="show_map"),
    url("^create_user_form.html$", "createUser", name="create_user"),
    url("^edit/(?P<theId>[0-9a-z\-]+)/$", "updateUser", name="update_user"),
    url("^update_user.html$", "emailEditAddress", name="email_update_user_link"),
)

urlpatterns += patterns('django.views.generic.simple',
    (r'^edit/email_confirm.html$',TemplateView.as_view(template_name='email_confirm.html')),
)
