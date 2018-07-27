from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'admin'
urlpatterns = [
    path('', views.home_admin, name='home_admin'),
    path('admin/data', views.home_admin_data, name='home_admin_data'),
    path('logout_admin', views.logout_admin, name='logout_admin'),
    path('group_service', views.group_service, name='group_service'),
]