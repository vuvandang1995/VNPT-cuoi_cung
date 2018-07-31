from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'admin'
urlpatterns = [
    path('', views.home_admin, name='home_admin'),
    path('admin/data', views.home_admin_data, name='home_admin_data'),
    path('choose_leader/data', views.fullname_agent_choose_leader_data, name='fullname_agent_choose_leader_data'),
    path('logout_admin', views.logout_admin, name='logout_admin'),
    path('group_service', views.group_service, name='group_service'),
    path('manage_agent', views.manage_agent, name="manage_agent"),
    path('manage_agent/data', views.manage_agent_data, name="manage_agent_data"),
    path('services', views.manage_serivce, name='manage_serivce'),
    path('admin/leader', views.fullname_agent_data, name='fullname_agent_data'),
    path('statistic', views.statistic, name='statistic'),

]