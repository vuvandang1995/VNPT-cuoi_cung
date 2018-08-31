from django.conf.urls import include, url
from django.urls import path
from . import views

app_name = 'superadmin'
urlpatterns = [
    url(r'^$', views.user_login),
    url('home', views.home, name='home'),

    # url(r'register/$',views.register, name='register'),
    # url(r'login/$', views.user_login, name='login'),

    url(r'profile/$', views.user_profile, name='profile'),
    url(r'logout/$', views.user_logout, name='logout'),
    path(r'^resetpassword/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.resetpwd, name='resetpassword'),

    # url(r'chat/([0-9]{5})',views.chat, name='chat'),
    # url(r'update_status/$', views.update_status, name='update_status'),
    # url(r'edit_contact/([^@]+@[^@]+\.[^@]+)', views.edit_contact, name='edit_contact'),
    # url(r'add_contact/$', views.add_contact, name='add_contact'),
]
