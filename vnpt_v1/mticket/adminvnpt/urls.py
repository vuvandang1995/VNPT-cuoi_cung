from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'admin'
urlpatterns = [
    path('', views.home_admin, name='home_admin'),
    path('data_line_year_<int:year>_<str:service>', views.home_admin_data_line_year, name='home_admin_data_line_year'),
    path('data_line_month_<int:month>_<int:year>_<str:service>', views.home_admin_data_line_month, name='home_admin_data_line_month'),
    path('data_pie_year_<int:year>_<str:service>', views.home_admin_data_pie_year, name='home_admin_data_pie_year'),
    path('data_pie_month_<int:month>_<int:year>_<str:service>', views.home_admin_data_pie_month, name='home_admin_data_pie_month'),
    path('choose_leader/data', views.fullname_agent_choose_leader_data, name='fullname_agent_choose_leader_data'),
    path('logout_admin', views.logout_admin, name='logout_admin'),
    path('group_service', views.group_service, name='group_service'),
    path('manage_agent', views.manage_agent, name="manage_agent"),
    path('manage_agent/data', views.manage_agent_data, name="manage_agent_data"),
    path('services', views.manage_serivce, name='manage_serivce'),
    path('admin/leader', views.fullname_agent_data, name='fullname_agent_data'),
    path('statistic_week', views.statistic_week, name='statistic_week'),
    path('statistic_month', views.statistic_month, name='statistic_month'),
    path('statistic_year', views.statistic_year, name='statistic_year'),
    path('statistic_data_agent_<int:kind>_<str:time>', views.statistic_data_agent, name='statistic_data_agent'),
    path('statistic_data_call_center_<int:kind>_<str:time>', views.statistic_data_call_center, name='statistic_data_call_center'),
    path('statistic_data_service_<int:kind>_<str:time>', views.statistic_data_service, name='statistic_data_service'),

]