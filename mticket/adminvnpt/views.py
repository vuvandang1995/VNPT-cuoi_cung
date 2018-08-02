from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from django.http import HttpResponseRedirect, HttpResponse
from django.http import JsonResponse
from user.views import EmailThread
from user.models import *
from .forms import ForwardForm, AddForm
from django.core.mail import EmailMessage
import simplejson as json
from django.utils.safestring import mark_safe
import json
import string
import os
from datetime import datetime
from datetime import timedelta
import pytz

utc=pytz.UTC
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits
# Create your views here.


def home_admin(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        content = {
                    'admin': admin,
                    'today': timezone.now().date(),
                    'agent_name': mark_safe(json.dumps(admin.username)),
                    'fullname': mark_safe(json.dumps(admin.fullname)),
                    'service': Services.objects.all(),
                   }
        return render(request, 'admin/chart.html', content)
    else:
        return redirect('/')


def home_admin_data_line_year(request, year, service):
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    labels = []
    data = []
    if service != 'all':
        sv = Services.objects.get(name=service)
        if year == year_now:
            for i in range(1, month_now+1):
                labels.append('Tháng ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, serviceid=sv, date_close__month=i, status=3).count())
        elif year < year_now:
            for i in range(1, 13):
                labels.append('Tháng ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, serviceid=sv, date_close__month=i, status=3).count())
        else:
            for i in range(1, 13):
                labels.append('Tháng ' + str(i))
                data.append(0)
    else:
        if year == year_now:
            for i in range(1, month_now+1):
                labels.append('Tháng ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, date_close__month=i, status=3).count())
        elif year < year_now:
            for i in range(1, 13):
                labels.append('Tháng ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, date_close__month=i, status=3).count())
        else:
            for i in range(1, 13):
                labels.append('Tháng ' + str(i))
                data.append(0)
    datasets = [{"label": 'Sự cố',
                 "backgroundColor": 'rgba(255, 0, 0, 1)',
                 "borderColor": 'rgba(255, 0, 0, 0.4)',
                 "data": data,
                 "fill": 'false',
                 }]
    big_data = {
        "labels": labels,
        "datasets": datasets,
    }
    return JsonResponse(big_data, safe=False)


def home_admin_data_line_month(request, month, year, service):
    day_now = int(timezone.now().day)
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    labels = []
    data = []
    if service != 'all':
        sv = Services.objects.get(name=service)
        if year == year_now:
            if month == month_now:
                for i in range(1, day_now+1):
                    labels.append('Ngày ' + str(i))
                    data.append(Tickets.objects.filter(date_close__year=year, serviceid=sv, date_close__month=month, date_close__day=i,
                                                       status=3).count())
            elif month < month_now:
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    day_range = 31
                elif month == 2:
                    if year%4 == 0:
                        day_range = 29
                    else:
                        day_range = 28
                else:
                    day_range = 30
                for i in range(1, day_range+1):
                    labels.append('Ngày ' + str(i))
                    data.append(Tickets.objects.filter(date_close__year=year, serviceid=sv, date_close__month=month,
                                                       date_close__day=i, status=3).count())
            else:
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    day_range = 31
                elif month == 2:
                    if year%4 == 0:
                        day_range = 29
                    else:
                        day_range = 28
                else:
                    day_range = 30
                for i in range(1, day_range+1):
                    labels.append('Ngày ' + str(i))
                    data.append(0)
        elif year < year_now:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day_range = 31
            elif month == 2:
                if year % 4 == 0:
                    day_range = 29
                else:
                    day_range = 28
            else:
                day_range = 30
            for i in range(1, day_range + 1):
                labels.append('Ngày ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, serviceid=sv,date_close__month=month,
                                                   date_close__day=i, status=3).count())
        else:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day_range = 31
            elif month == 2:
                if year % 4 == 0:
                    day_range = 29
                else:
                    day_range = 28
            else:
                day_range = 30
            for i in range(1, day_range + 1):
                labels.append('Ngày ' + str(i))
                data.append(0)
    else:
        if year == year_now:
            if month == month_now:
                for i in range(1, day_now+1):
                    labels.append('Ngày ' + str(i))
                    data.append(Tickets.objects.filter(date_close__year=year, date_close__month=month, date_close__day=i,
                                                       status=3).count())
            elif month < month_now:
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    day_range = 31
                elif month == 2:
                    if year%4 == 0:
                        day_range = 29
                    else:
                        day_range = 28
                else:
                    day_range = 30
                for i in range(1, day_range+1):
                    labels.append('Ngày ' + str(i))
                    data.append(Tickets.objects.filter(date_close__year=year, date_close__month=month,
                                                       date_close__day=i, status=3).count())
            else:
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    day_range = 31
                elif month == 2:
                    if year%4 == 0:
                        day_range = 29
                    else:
                        day_range = 28
                else:
                    day_range = 30
                for i in range(1, day_range+1):
                    labels.append('Ngày ' + str(i))
                    data.append(0)
        elif year < year_now:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day_range = 31
            elif month == 2:
                if year % 4 == 0:
                    day_range = 29
                else:
                    day_range = 28
            else:
                day_range = 30
            for i in range(1, day_range + 1):
                labels.append('Ngày ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, date_close__month=month,
                                                   date_close__day=i, status=3).count())
        else:
            if month in [1, 3, 5, 7, 8, 10, 12]:
                day_range = 31
            elif month == 2:
                if year % 4 == 0:
                    day_range = 29
                else:
                    day_range = 28
            else:
                day_range = 30
            for i in range(1, day_range + 1):
                labels.append('Ngày ' + str(i))
                data.append(0)
    datasets = [{"label": 'Sự cố',
                 "backgroundColor": 'rgba(255, 0, 0, 1)',
                 "borderColor": 'rgba(255, 0, 0, 0.4)',
                 "data": data,
                 "fill": 'false',
                 }]
    big_data = {
        "labels": labels,
        "datasets": datasets,
    }
    return JsonResponse(big_data, safe=False)


def home_admin_data_pie_year(request, year, service):
    year_now = int(timezone.now().year)
    if service != 'all':
        sv = Services.objects.get(name=service)
        if year <= year_now:
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, serviceid=sv, date_close__year=year)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, serviceid=sv, date_close__year=year)
            tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
            tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
            tkid_dung = [tk.ticketid for tk in tklog_dung_han]
            tkid_qua = []
            tkid_cham = []
            open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                       "nhận xử lý yêu cầu được giao từ quản trị viên",
                       'tạo mới và tự xử lý yêu cầu']
            for tk in tklog_sai_han:
                tkid = tk.ticketid
                tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                if len(tik) == 0:
                    continue
                else:
                    date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                    date_end = tk.ticketid.dateend
                    if date_open <= date_end:
                        tkid_cham.append(tk.ticketid)
                    else:
                        tkid_qua.append(tk.ticketid)
            dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
            cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
            qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
            data = [dung, cham, qua]
        else:
            data = [0, 0, 0]
    else:
        if year <= year_now:
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year)
            tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
            tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
            tkid_dung = [tk.ticketid for tk in tklog_dung_han]
            tkid_qua = []
            tkid_cham = []
            open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                       "nhận xử lý yêu cầu được giao từ quản trị viên",
                       'tạo mới và tự xử lý yêu cầu']
            for tk in tklog_sai_han:
                tkid = tk.ticketid
                tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                if len(tik) == 0:
                    continue
                else:
                    date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                    date_end = tk.ticketid.dateend
                    if date_open <= date_end:
                        tkid_cham.append(tk.ticketid)
                    else:
                        tkid_qua.append(tk.ticketid)
            dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
            cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
            qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
            data = [dung, cham, qua]
        else:
            data = [0, 0, 0]
    datasets = [{"label": 'Sự cố',
                 "backgroundColor": [
                    'rgba(255,127,80, 0.5)',
                    'rgba(0, 255, 0, 0.5)',
                    'rgba(0, 0, 255, 0.5)',
                    ],
                 "borderColor": [
                    'rgba(255,127,80, 1)',
                    'rgba(0, 255, 0, 1)',
                    'rgba(0, 0, 255, 1)',
                    ],
                 "data": data,
                 "fill": 'false',
                 }]
    big_data = {
        "labels": ['Đúng hạn', 'Chậm', 'Quá hạn'],
        "datasets": datasets,
    }
    return JsonResponse(big_data, safe=False)


def home_admin_data_pie_month(request, month, year, service):
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    if service != 'all':
        sv = Services.objects.get(name=service)
        if year == year_now:
            if month <= month_now:
                tk_dung_han = Tickets.objects.filter(expired=0, status=3, serviceid=sv,date_close__year=year, date_close__month=month)
                tk_sai_han = Tickets.objects.filter(expired=1, status=3, serviceid=sv,date_close__year=year, date_close__month=month)
                tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
                tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
                tkid_dung = [tk.ticketid for tk in tklog_dung_han]
                tkid_qua = []
                tkid_cham = []
                open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                           "nhận xử lý yêu cầu được giao từ quản trị viên",
                           'tạo mới và tự xử lý yêu cầu']
                for tk in tklog_sai_han:
                    tkid = tk.ticketid
                    tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                    if len(tik) == 0:
                        continue
                    else:
                        date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                        date_end = tk.ticketid.dateend
                        if date_open <= date_end:
                            tkid_cham.append(tk.ticketid)
                        else:
                            tkid_qua.append(tk.ticketid)
                dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
                cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
                qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
                data = [dung, cham, qua]
            else:
                data = [0, 0, 0]
        elif year < year_now:
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, serviceid=sv,date_close__year=year, date_close__month=month)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, serviceid=sv,date_close__year=year, date_close__month=month)
            tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
            tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
            tkid_dung = [tk.ticketid for tk in tklog_dung_han]
            tkid_qua = []
            tkid_cham = []
            open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                       "nhận xử lý yêu cầu được giao từ quản trị viên",
                       'tạo mới và tự xử lý yêu cầu']
            for tk in tklog_sai_han:
                tkid = tk.ticketid
                tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                if len(tik) == 0:
                    continue
                else:
                    date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                    date_end = tk.ticketid.dateend
                    if date_open <= date_end:
                        tkid_cham.append(tk.ticketid)
                    else:
                        tkid_qua.append(tk.ticketid)
            dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
            cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
            qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
            data = [dung, cham, qua]
        else:
            data = [0, 0, 0]
    else:
        if year == year_now:
            if month <= month_now:
                tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year, date_close__month=month)
                tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year, date_close__month=month)
                tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
                tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
                tkid_dung = [tk.ticketid for tk in tklog_dung_han]
                tkid_qua = []
                tkid_cham = []
                open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                           "nhận xử lý yêu cầu được giao từ quản trị viên",
                           'tạo mới và tự xử lý yêu cầu']
                for tk in tklog_sai_han:
                    tkid = tk.ticketid
                    tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                    if len(tik) == 0:
                        continue
                    else:
                        date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                        date_end = tk.ticketid.dateend
                        if date_open <= date_end:
                            tkid_cham.append(tk.ticketid)
                        else:
                            tkid_qua.append(tk.ticketid)
                dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
                cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
                qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
                data = [dung, cham, qua]
            else:
                data = [0, 0, 0]
        elif year < year_now:
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year, date_close__month=month)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year, date_close__month=month)
            tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
            tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
            tkid_dung = [tk.ticketid for tk in tklog_dung_han]
            tkid_qua = []
            tkid_cham = []
            open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                       "nhận xử lý yêu cầu được giao từ quản trị viên",
                       'tạo mới và tự xử lý yêu cầu']
            for tk in tklog_sai_han:
                tkid = tk.ticketid
                tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                if len(tik) == 0:
                    continue
                else:
                    date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                    date_end = tk.ticketid.dateend
                    if date_open <= date_end:
                        tkid_cham.append(tk.ticketid)
                    else:
                        tkid_qua.append(tk.ticketid)
            dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
            cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
            qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
            data = [dung, cham, qua]
        else:
            data = [0, 0, 0]
    datasets = [{"label": 'Sự cố',
                 "backgroundColor": [
                    'rgba(255,127,80, 0.5)',
                    'rgba(0, 255, 0, 0.5)',
                    'rgba(0, 0, 255, 0.5)',
                    ],
                 "borderColor": [
                    'rgba(255,127,80, 1)',
                    'rgba(0, 255, 0, 1)',
                    'rgba(0, 0, 255, 1)',
                    ],
                 "data": data,
                 "fill": 'false',
                 }]
    big_data = {
        "labels": ['Đúng hạn', 'Chậm', 'Quá hạn'],
        "datasets": datasets,
    }
    return JsonResponse(big_data, safe=False)


def logout_admin(request):
    del request.session['admin']
    return redirect("/")


def group_service(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        groupservice = GroupServices.objects.all()
        list_tp = {}
        for gs in groupservice:
            tps = Services.objects.filter(groupserviceid=gs)
            list_tp[gs.id] = [tp.name for tp in tps]
        content = {
                   'list_tp': list_tp,
                   'admin': admin,
                   'today': timezone.now().date(),
                   'groupservice': groupservice,
                   'fullname': mark_safe(json.dumps(admin.fullname)),
                   'agent_name': mark_safe(json.dumps(admin.username)),}
        if request.method == 'POST':
            if 'addname' in request.POST:
                if request.POST['gsid'] == '':
                    GroupServices.objects.create(name=request.POST['addname'])
                else:
                    gs = GroupServices.objects.get(id=request.POST['gsid'])
                    gs.name = request.POST['addname']
                    gs.save()
            elif 'delete' in request.POST:
                GroupServices.objects.filter(id=request.POST['delete']).delete()
            return redirect("/admin/group_service")
        else:
            return render(request, 'admin/group_service.html', content)
    else:
        return redirect('/')


def manage_agent(request):
    if request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        agent = Agents.objects.get(username=request.session['admin'])
        svag = ServiceAgent.objects.filter(agentid=agent)
        list_tp = ""
        for tp1 in svag:
            list_tp += str(tp1.serviceid.name) + "!"
        users = Agents.objects.all()
        if request.method == 'POST':
            if 'position' in request.POST:
                user = Agents.objects.get(id=request.POST['agid'])
                user.position = request.POST['position']
                user.save()
            else:
                user = Agents.objects.get(id=request.POST['agid'])
                user.status = request.POST['stt']
                user.save()
        
        return render(request,"admin/manage_agent.html",{
                    'user':users, 
                    'agent_name': mark_safe(json.dumps(agent.username)), 
                    'fullname': mark_safe(json.dumps(agent.fullname)),
                    'list_tp': mark_safe(json.dumps(list_tp))})
    else:
        return redirect("/")


def manage_agent_data(request):
    if request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        users = Agents.objects.all()
        data = []
        for us in users:
            if us.status == 0:
                st = r'''<p id="stt''' + str(us.id) +'''"><span class="label label-danger">Khóa</span></p>'''
                option = r'''<p id="button''' + str(us.id) +'''"><button id="''' + str(us.id) + '''" class="unblock btn btn-success" type="button" data-toggle="tooltip" title="mở khóa" ><span class="glyphicon glyphicon glyphicon-ok" ></span> Mở khóa</button></p>'''
            else:
                st = r'''<p id="stt''' + str(us.id) +'''"><span class="label label-success">Kích hoạt</span></p>'''
                option = r'''<p id="button''' + str(us.id) +'''"><button id="''' + str(us.id) + '''" class="block btn btn-danger" type="button" data-toggle="tooltip" title="Khóa" ><span class="glyphicon glyphicon-lock" ></span> Khóa</button></p>'''
            if us.position == 0:
                position = '''
                        <select name="''' + str(us.id) +'''" class="form-control position" >
                            <option value="0" name="Call Center">Call Center</option>
                            <option value="1" name="Nhân viên xử lý">Nhân viên xử lý</option>
                            <option value="2" name="Quản trị viên">Quản trị viên</option>
                            <option value="3" name="Admin">Admin</option>
                            <option value="4" name="Phó Quản trị viên">Phó Quản trị viên</option>
                        </select>
                        '''
            elif us.position == 1:
                position = '''
                        <select name="''' + str(us.id) +'''" class="form-control position" >
                            <option value="1" name="Nhân viên xử lý">Nhân viên xử lý</option>
                            <option value="0" name="Call Center">Call Center</option>
                            <option value="2" name="Quản trị viên">Quản trị viên</option>
                            <option value="3" name="Admin">Admin</option>
                            <option value="4" name="Phó Quản trị viên">Phó Quản trị viên</option>
                        </select>
                        '''
            elif us.position == 2:
                position = '''
                        <select name="''' + str(us.id) +'''" class="form-control position" >
                            <option value="2" name="Quản trị viên">Quản trị viên</option>
                            <option value="0" name="Call Center">Call Center</option>
                            <option value="1" name="Nhân viên xử lý">Nhân viên xử lý</option>
                            <option value="3" name="Admin">Admin</option>
                            <option value="4" name="Phó Quản trị viên">Phó Quản trị viên</option>
                        </select>
                        '''
            elif us.position == 3:
                position = '''
                        <select name="''' + str(us.id) +'''" class="form-control position" >
                            <option value="3" name="Admin">Admin</option>
                            <option value="0" name="Call Center">Call Center</option>
                            <option value="1" name="Nhân viên xử lý">Nhân viên xử lý</option>
                            <option value="2" name="Quản trị viên">Quản trị viên</option>
                            <option value="4" name="Phó Quản trị viên">Phó Quản trị viên</option>
                        </select>
                        '''
            elif us.position == 4:
                position = '''
                        <select name="''' + str(us.id) +'''" class="form-control position" >
                            <option value="4" name="Phó Quản trị viên">Phó Quản trị viên</option>
                            <option value="0" name="Call Center">Call Center</option>
                            <option value="1" name="Nhân viên xử lý">Nhân viên xử lý</option>
                            <option value="2" name="Quản trị viên">Quản trị viên</option>
                            <option value="3" name="Admin">Admin</option>
                        </select>
                        '''
            data.append([us.id, us.fullname, us.email, us.username, st, position, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def manage_serivce(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        agent = Agents.objects.exclude(username=request.session['admin'])
        gpsv = GroupServices.objects.all()
        sv = Services.objects.all()
        list_ag = {}
        downtime = {}
        for s in sv:
            svag = ServiceAgent.objects.filter(serviceid=s, agentid__in=agent)
            list_ag[s.name] = [a.agentid for a in svag]
            t = s.downtime
            if t < 60:
                downtime[s.id] = str(t) + ' phút'
            elif t < 1440:
                downtime[s.id] = str(t // 60) + ' giờ ' + str(t % 60) + ' phút '
            else:
                downtime[s.id] = str(t // 1440) + ' ngày ' + str(t % 1440 // 60) + ' giờ ' + str(t % 1440 % 60) + ' phút '
        content = {'service': sv,
                   'downtime': downtime,
                   'list_ag': list_ag,
                   'admin': admin,
                   'today': timezone.now().date(),
                   'agent_name': mark_safe(json.dumps(admin.username)),
                   'fullname': mark_safe(json.dumps(admin.fullname)), 
                   'agent':agent,
                   'gpsv': gpsv,
                   'service': sv}
        if request.method == 'POST':
            if 'close' in request.POST:
                svid = request.POST['close']
                sv = Services.objects.get(id=svid)
                leader = Agents.objects.get(username=request.POST['leader'])
                if sv.status == 0:
                    sv.status = 1
                else:
                    sv.status = 0
                if leader.position == 2:
                    leader.position = 1
                elif leader.position == 1:
                    leader.position = 2
                leader.save()
                sv.save()
            elif 'delete' in request.POST:
                svid = request.POST['delete']
                sv = Services.objects.get(id=svid)
                sv.delete()
                leader = Agents.objects.get(username=request.POST['leader'])
                leader.position = 1
                leader.save()
            elif 'add_service' in request.POST:
                list_agent = request.POST['list_agent[]']
                list_agent = json.loads(list_agent)
                if request.POST['svid'] == '0':
                    svname = request.POST['add_service']
                    description = request.POST['description']
                    leader = Agents.objects.get(username=request.POST['leader'])
                    downtime = request.POST['downtime']
                    sv = Services.objects.create(name=svname, description=description, leader=leader, downtime=downtime, groupserviceid=GroupServices.objects.get(id=request.POST['gpsv']))
                    if leader.position != 2:
                        leader.position = 2
                        leader.save()

                    if not list_agent:
                        pass
                    else:
                        for agentname in list_agent:
                            agent = Agents.objects.get(username=agentname)
                            svag = ServiceAgent.objects.create(agentid=agent, serviceid=sv)
                            agent.position = 1
                            agent.save()
                else:
                    sv = Services.objects.get(id=request.POST['svid'])
                    sv.name = request.POST['add_service']
                    sv.description = request.POST['description']
                    leader_old = Agents.objects.get(id=sv.leader.id)
                    leader_new = Agents.objects.get(username=request.POST['leader'])
                    sv.leader = leader_new
                    sv.downtime = request.POST['downtime']
                    if leader_new.position != 2:
                        leader_new.position = 2
                        leader_new.save()
                    sv.save()

                    count_sv = Services.objects.filter(leader=leader_old).count()
                    if count_sv < 1:
                        leader_old.position = 1
                        leader_old.save()

                    if not list_agent:
                        try:
                            svag1 = ServiceAgent.objects.filter(serviceid=sv)
                            svag1.delete()
                        except:
                            pass
                    else:
                        try:
                            svag1 = ServiceAgent.objects.filter(serviceid=sv)
                            svag1.delete()
                        except:
                            pass
                        for agentname in list_agent:
                            agent = Agents.objects.get(username=agentname)
                            svag = ServiceAgent.objects.create(agentid=agent, serviceid=sv)
        return render(request, 'admin/manage_service.html', content)
    else:
        return redirect('/')


def fullname_agent_data(request):
    if request.session.has_key('admin'):
        agent_leader = Agents.objects.exclude(position__in=[2,3])
        list_agent_leader = []
        for ag in agent_leader:
            if ag.status == 1:
                list_agent_leader.append({"username": ag.username, "fullname": ag.fullname})
        return JsonResponse(list_agent_leader, safe=False)
    else:
        return redirect('/')


def fullname_agent_choose_leader_data(request):
    if request.session.has_key('admin'):
        agent_leader = Agents.objects.exclude(position=3 )
        list_agent_leader = []
        for ag in agent_leader:
            if ag.status == 1:
                list_agent_leader.append({"username": ag.username, "fullname": ag.fullname, 'total_tk': count_tk_to_choose_leader(ag.username)})
        return JsonResponse(list_agent_leader, safe=False)
    else:
        return redirect('/')


def statistic_week(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        content = {
                   'admin': admin,
                   'today': timezone.now().date(),
                   'agent_name': mark_safe(json.dumps(admin.username)),
                   'fullname': mark_safe(json.dumps(admin.fullname)),}
        return render(request, 'admin/statistic_week.html', content)
    else:
        return redirect('/')


def statistic_month(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        year = timezone.now().year
        month = timezone.now().month
        content = {
                   'admin': admin,
                   'today': timezone.now().date(),
                   'month': month,
                   'year': year,
                   'agent_name': mark_safe(json.dumps(admin.username)),
                   'fullname': mark_safe(json.dumps(admin.fullname)),}
        return render(request, 'admin/statistic_month.html', content)
    else:
        return redirect('/')


def statistic_year(request):
    if request.session.has_key('admin'):
        admin = Agents.objects.get(username=request.session['admin'])
        year = timezone.now().year
        content = {
                   'admin': admin,
                   'today': timezone.now().date(),
                   'year': year,
                   'agent_name': mark_safe(json.dumps(admin.username)),
                   'fullname': mark_safe(json.dumps(admin.fullname)),}
        return render(request, 'admin/statistic_year.html', content)
    else:
        return redirect('/')


def statistic_data_agent(request, kind, time):
    if request.session.has_key('admin'):
        agents = Agents.objects.filter(position__in=[1, 4])
        if kind == 3:
            year = time
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year)
        elif kind == 2:
            month, year = str(time).split('_')
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year, date_close__month=month)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year, date_close__month=month)
        else:
            start_date = timezone.datetime.strptime(time, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=7)
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__range=(start_date, end_date))
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__range=(start_date, end_date))
        tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
        tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
        list_ag = []
        tkid_dung = [tk.ticketid for tk in tklog_dung_han]
        tkid_qua = []
        tkid_cham = []
        open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                   "nhận xử lý yêu cầu được giao từ quản trị viên"]
        for tk in tklog_sai_han:
            tkid = tk.ticketid
            tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
            if len(tik)==0:
                continue
            else:
                date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                date_end = tk.ticketid.dateend
                if date_open <= date_end:
                    tkid_cham.append(tk.ticketid)
                else:
                    tkid_qua.append(tk.ticketid)
        for ag in agents:
            dung = TicketAgent.objects.filter(agentid=ag, ticketid__in=tkid_dung).count()
            qua = TicketAgent.objects.filter(agentid=ag, ticketid__in=tkid_qua).count()
            cham = TicketAgent.objects.filter(agentid=ag, ticketid__in=tkid_cham).count()
            list_ag.append([ag.fullname, dung, cham, qua, dung+cham+qua])
        data = {"data": list_ag}
        datas = json.loads(json.dumps(data))
        return JsonResponse(datas, safe=False)


def statistic_data_call_center(request, kind, time):
    if request.session.has_key('admin'):
        agents = Agents.objects.filter(position=0)
        list_ag = []
        if kind == 3:
            year = time
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year)
        elif kind == 2:
            month, year = str(time).split('_')
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__year=year, date_close__month=month)
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__year=year, date_close__month=month)
        else:
            start_date = timezone.datetime.strptime(time, "%Y-%m-%d").date()
            end_date = start_date + timedelta(days=7)
            tk_dung_han = Tickets.objects.filter(expired=0, status=3, date_close__range=(start_date, end_date))
            tk_sai_han = Tickets.objects.filter(expired=1, status=3, date_close__range=(start_date, end_date))
        tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
        tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
        tkid_dung = [tk.ticketid for tk in tklog_dung_han]
        tkid_cham = [tk.ticketid for tk in tklog_sai_han]
        for ag in agents:
            # gui_di = TicketLog.objects.filter(action='tạo mới yêu cầu', agentid=ag,
            #                                   date__month=month, date__year=year).count()
            dung = TicketAgent.objects.filter(agentid=ag, ticketid__in=tkid_dung).count()
            cham = TicketAgent.objects.filter(agentid=ag, ticketid__in=tkid_cham).count()
            list_ag.append([ag.fullname, dung, cham, 0, dung+cham])
        data = {"data": list_ag}
        datas = json.loads(json.dumps(data))
        return JsonResponse(datas, safe=False)


def statistic_data_service(request, kind, time):
    if request.session.has_key('admin'):
        service = Services.objects.all()
        list_sv = []
        for sv in service:
            if kind == 3:
                year = time
                tk_dung_han = Tickets.objects.filter(expired=0, serviceid=sv, status=3, date_close__year=year)
                tk_sai_han = Tickets.objects.filter(expired=1, serviceid=sv, status=3, date_close__year=year)
            elif kind == 2:
                month, year = str(time).split('_')
                tk_dung_han = Tickets.objects.filter(expired=0, serviceid=sv, status=3, date_close__year=year,
                                                     date_close__month=month)
                tk_sai_han = Tickets.objects.filter(expired=1, serviceid=sv, status=3, date_close__year=year,
                                                    date_close__month=month)
            else:
                start_date = timezone.datetime.strptime(time, "%Y-%m-%d").date()
                end_date = start_date + timedelta(days=7)
                tk_dung_han = Tickets.objects.filter(expired=0, serviceid=sv, status=3, date_close__range=(start_date, end_date))
                tk_sai_han = Tickets.objects.filter(expired=1, serviceid=sv, status=3, date_close__range=(start_date, end_date))

            tklog_dung_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_dung_han)
            tklog_sai_han = TicketLog.objects.filter(action='đóng yêu cầu', ticketid__in=tk_sai_han)
            tkid_dung = [tk.ticketid for tk in tklog_dung_han]
            tkid_qua = []
            tkid_cham = []
            open_tk = ['nhận xử lý yêu cầu', 'xử lý lại yêu cầu', 'mở lại yêu cầu',
                       "nhận xử lý yêu cầu được giao từ quản trị viên",
                       'tạo mới và tự xử lý yêu cầu']
            for tk in tklog_sai_han:
                tkid = tk.ticketid
                tik = TicketLog.objects.filter(action__in=open_tk, ticketid=tkid).order_by("-id")
                if len(tik) == 0:
                    continue
                else:
                    date_open = timezone.datetime.combine(tik[0].date, tik[0].time).replace(tzinfo=utc)
                    date_end = tk.ticketid.dateend
                    if date_open <= date_end:
                        tkid_cham.append(tk.ticketid)
                    else:
                        tkid_qua.append(tk.ticketid)
            dung = TicketAgent.objects.filter(ticketid__in=tkid_dung).count()
            qua = TicketAgent.objects.filter(ticketid__in=tkid_qua).count()
            cham = TicketAgent.objects.filter(ticketid__in=tkid_cham).count()
            list_sv.append([sv.groupserviceid.name, sv.name, dung, cham, qua, dung+cham+qua])
        data = {"data": list_sv}
        datas = json.loads(json.dumps(data))
        return JsonResponse(datas, safe=False)
