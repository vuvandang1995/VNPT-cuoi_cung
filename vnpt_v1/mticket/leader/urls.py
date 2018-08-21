
from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

app_name = 'leader'
urlpatterns = [
    path('', views.home_chart, name="home_chart"),
    path('data_line_year_<int:year>_<str:service>', views.data_line_year, name='data_line_year'),
    path('data_line_month_<int:month>_<int:year>_<str:service>', views.data_line_month, name='data_line_month'),
    path('data_pie_year_<int:year>_<str:service>', views.data_pie_year, name='data_pie_year'),
    path('data_pie_month_<int:month>_<int:year>_<str:service>', views.data_pie_month, name='data_pie_month'),
    path('home_leader', views.home_leader, name="home_leader"),
    path('data', views.leader_agent_data, name="leader_agent_data"),
    path('home_leader/data/<str:servicename>', views.home_leader_data, name="home_leader_data"),
    path('manage_agent', views.leader_manage_agent, name="leader_manage_agent"),
    path('profile', views.leader_profile, name="leader_profile"),
    path('logout_leader/', views.logout_leader, name='logout_leader'),
    path('leader_to_agent', views.leader_to_agent, name='leader_to_agent'),
]