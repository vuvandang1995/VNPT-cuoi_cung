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


def logout_leader(request):
    del request.session['leader']
    return redirect("/")


def home_leader(request):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        if Agents.objects.get(username=request.session['leader']).position == 2:
            leader = Agents.objects.get(username=request.session['leader'])
            list_topic = Services.objects.filter(leader=leader)
            list_ticket = {}
            list_ag = {}
            for tp in list_topic:
                list_ticket[tp] = Tickets.objects.filter(serviceid=tp)
                ag = ServiceAgent.objects.filter(serviceid=tp)
                list_ag[tp.name] = [a.agentid for a in ag]
            content = {'tickets': list_ticket,
                    'leng': len(list_topic),
                    'topic': list_topic,
                    'list_ag': list_ag,
                    'agent_name': mark_safe(json.dumps(leader.username)),
                    'fullname': mark_safe(json.dumps(leader.fullname)),
                    'topic_all': Services.objects.all(),
                    'leader': leader
                    }
            if request.method == 'POST':
                if 'close' in request.POST:
                    ticketid = request.POST['close']
                    tk = Tickets.objects.get(id=ticketid)
                    if tk.status == 3:
                        if not TicketAgent.objects.filter(ticketid=tk):
                            tk.status = 0
                            action = "mở lại yêu cầu"
                        else:
                            tk.status = 1
                            action = "xử lý lại yêu cầu"
                    else:
                        tk.status = 3
                        action = "đóng yêu cầu"
                    tk.save()
                    TicketLog.objects.create(agentid=leader, ticketid=tk,
                                            action=action,
                                            date=timezone.now().date(),
                                            time=timezone.now().time())
                elif 'delete' in request.POST:
                    ticketid = request.POST['delete']
                    tk = Tickets.objects.get(id=ticketid)
                    tk.delete()
                    try:
                        os.remove(r'notification/chat/chat_' + ticketid + '.txt')
                    except:
                        pass
                elif 'ticketid' in request.POST:
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    ticketid = request.POST['ticketid']
                    if not list_agent:
                        try:
                            tk = Tickets.objects.get(id=ticketid)
                            tkag1 = TicketAgent.objects.filter(ticketid=tk)
                            tkag1.delete()
                            tk.status = 0
                            tk.save()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            tklog = TicketLog.objects.filter(action=action)
                            tklog.delete()
                        except:
                            tk.status = 0
                            tk.save()
                    else:
                        try:
                            tk = Tickets.objects.get(id=ticketid)
                            tkag1 = TicketAgent.objects.filter(ticketid=tk)
                            tkag1.delete()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            tklog = TicketLog.objects.filter(action=action)
                            tklog.delete()
                        except:
                            pass
                        for agentid in list_agent:
                            agent = Agents.objects.get(username=agentid)
                            tk = Tickets.objects.get(id=ticketid)
                            tkag = TicketAgent(agentid=agent, ticketid=tk)
                            tkag.save()
                            tk.status = 1
                            tk.save()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            if agent.receive_email == 1:
                                email = EmailMessage(
                                    'Chuyển yêu cầu',
                                    render_to_string('agent/mail/forward_mail_leader.html',
                                                    {'receiver': agent,
                                                    'domain': (get_current_site(request)).domain,
                                                    'sender': 'Leader'}),
                                    to=[agent.email],
                                )
                                thread = EmailThread(email)
                                thread.start()
                            TicketLog.objects.create(agentid=agent, ticketid=tk,
                                                    action=action,
                                                    date=timezone.now().date(),
                                                    time=timezone.now().time())
                elif 'ticketid_change' in request.POST:
                    tp = Services.objects.get(id=request.POST['serviceid'])
                    tk = Tickets.objects.get(id=request.POST['ticketid_change'])
                    tk.serviceid = tp
                    tk.save()
            return render(request, 'leader/home_leader.html', content)
        else:
            leader = Agents.objects.get(username=request.session['leader'])
            list_topic = Services.objects.filter(leader_bk=leader)
            list_ticket = {}
            list_ag = {}
            for tp in list_topic:
                list_ticket[tp] = Tickets.objects.filter(serviceid=tp)
                ag = ServiceAgent.objects.filter(serviceid=tp)
                list_ag[tp.name] = [a.agentid for a in ag]
            content = {'tickets': list_ticket,
                    'leng': len(list_topic),
                    'topic': list_topic,
                    'list_ag': list_ag,
                    'agent_name': mark_safe(json.dumps(leader.username)),
                    'fullname': mark_safe(json.dumps(leader.fullname)),
                    'topic_all': Services.objects.all(),
                    'leader': leader
                    }
            if request.method == 'POST':
                if 'close' in request.POST:
                    ticketid = request.POST['close']
                    tk = Tickets.objects.get(id=ticketid)
                    if tk.status == 3:
                        if not TicketAgent.objects.filter(ticketid=tk):
                            tk.status = 0
                            action = "mở lại yêu cầu"
                        else:
                            tk.status = 1
                            action = "xử lý lại yêu cầu"
                    else:
                        tk.status = 3
                        action = "đóng yêu cầu"
                    tk.save()
                    TicketLog.objects.create(agentid=leader, ticketid=tk,
                                            action=action,
                                            date=timezone.now().date(),
                                            time=timezone.now().time())
                elif 'delete' in request.POST:
                    ticketid = request.POST['delete']
                    tk = Tickets.objects.get(id=ticketid)
                    tk.delete()
                    try:
                        os.remove(r'notification/chat/chat_' + ticketid + '.txt')
                    except:
                        pass
                elif 'ticketid' in request.POST:
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    ticketid = request.POST['ticketid']
                    if not list_agent:
                        try:
                            tk = Tickets.objects.get(id=ticketid)
                            tkag1 = TicketAgent.objects.filter(ticketid=tk)
                            tkag1.delete()
                            tk.status = 0
                            tk.save()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            tklog = TicketLog.objects.filter(action=action)
                            tklog.delete()
                        except:
                            tk.status = 0
                            tk.save()
                    else:
                        try:
                            tk = Tickets.objects.get(id=ticketid)
                            tkag1 = TicketAgent.objects.filter(ticketid=tk)
                            tkag1.delete()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            tklog = TicketLog.objects.filter(action=action)
                            tklog.delete()
                        except:
                            pass
                        for agentid in list_agent:
                            agent = Agents.objects.get(username=agentid)
                            tk = Tickets.objects.get(id=ticketid)
                            tkag = TicketAgent(agentid=agent, ticketid=tk)
                            tkag.save()
                            tk.status = 1
                            tk.save()
                            action = "nhận xử lý yêu cầu được giao từ quản trị viên"
                            if agent.receive_email == 1:
                                email = EmailMessage(
                                    'Chuyển yêu cầu',
                                    render_to_string('agent/mail/forward_mail_leader.html',
                                                    {'receiver': agent,
                                                    'domain': (get_current_site(request)).domain,
                                                    'sender': 'Leader'}),
                                    to=[agent.email],
                                )
                                thread = EmailThread(email)
                                thread.start()
                            TicketLog.objects.create(agentid=agent, ticketid=tk,
                                                    action=action,
                                                    date=timezone.now().date(),
                                                    time=timezone.now().time())
                elif 'ticketid_change' in request.POST:
                    tp = Services.objects.get(id=request.POST['serviceid'])
                    tk = Tickets.objects.get(id=request.POST['ticketid_change'])
                    tk.serviceid = tp
                    tk.save()
            return render(request, 'leader/home_leader.html', content)
    else:
        return redirect("/")


def home_leader_data(request, servicename):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        agent = Agents.objects.get(username=request.session['leader'])
        # list_topic = Services.objects.filter(leader=agent)
        # list_ticket = []
        # for tp in list_topic:
        sv = Services.objects.get(name=servicename)
        tksdpr = Tickets.objects.filter(serviceid=sv)
        data = []
        for tk in tksdpr:
            if tk.status == 0:
                status = r'<span class ="label label-danger" id="leader' + str(tk.id) + '">Chờ</span>'
                handler = '<p id="hd' + str(tk.id) + '">Nobody</p>'
                option = r'''<button type="button" class="btn btn-primary" id="''' + str(tk.id) + '''" data-toggle="tooltip" title="Mở / Đóng yêu cầu"><i class="fa fa-power-off"></i></button>
                        <button type="button" class="btn btn-danger" id="''' + str(tk.id) + '''" data-toggle="tooltip" title="Xóa yêu cầu"><i class="fa fa-trash-o"></i></button>
                        <button type="button" class="btn btn-info" data-title="forward" id="'''+str(tk.id)+'''"data-toggle="modal" data-target="#forward_modal"><i class="fa fa-share-square-o" data-toggle="tooltip" title="Chuyển tiếp" ></i></button>
                        <button type="button" class="btn btn-success" data-title="change" id="''' + str(tk.id) + '''"data-toggle="modal" data-target="#change_modal"><i class="fa fa-arrow-right" data-toggle="tooltip" title="Chuyển đổi dịch vụ" ></i></button>'''
                
            else:
                if tk.status == 1:
                    status = r'<span class ="label label-warning" id="leader' + str(tk.id) + '">Đang xử lý</span>'
                elif tk.status == 2:
                    status = r'<span class ="label label-success" id="leader' + str(tk.id) + '">Hoàn thành</span>'
                else:
                    if tk.expired == 0:
                        status = r'<span class ="label label-default" id="leader' + str(tk.id) + '">Đóng</span></br><span class ="label label-info">Đúng hạn</span>'
                    else:
                        status = r'<span class ="label label-default" id="leader' + str(tk.id) + '">Đóng</span></br><span class ="label label-warning">Quá hạn</span>'
                handler = '<p hidden id="hd' + str(tk.id) + '">'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.username + "<br>"
                handler += '</p><p>'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.fullname + "<br>"
                handler += '</p>'
                option = r'''<button type="button" class="btn btn-primary" id="''' + str(tk.id) + '''" data-toggle="tooltip" title="Mở / Đóng yêu cầu"><i class="fa fa-power-off"></i></button>
                        <button type="button" class="btn btn-danger" id="''' + str(tk.id) + '''" data-toggle="tooltip" title="Xóa yêu cầu"><i class="fa fa-trash-o"></i></button>
                        <button type="button" class="btn btn-info" data-title="forward" id="'''+str(tk.id)+'''"data-toggle="modal" data-target="#forward_modal"><i class="fa fa-share-square-o" data-toggle="tooltip" title="Chuyển tiếp" ></i></button>
                        <button disabled type="button" class="btn btn-success" data-title="change" id="''' + str(tk.id) + '''"data-toggle="modal" data-target="#change_modal"><i class="fa fa-arrow-right" data-toggle="tooltip" title="Chỉ có thể chuyển đổi dịch vụ khi yêu cầu đang chờ" ></i></button>'''
            downtime = '''<span class="downtime label label-warning" id="downtime-'''+str(tk.id)+'''"></span>'''
            idtk = r'''<button type="button" class="btn" data-toggle="modal" data-target="#''' + str(
                tk.id) + '''content">''' + str(tk.id) + '''</button>'''
            service = '<p id="tp' + str(tk.id) + '">' + tk.serviceid.name + '</p>' + '<input type="hidden" name="topicc'+str(tk.id)+'" value="'+str(tk.serviceid.id)+'">'
            
            sender = '<p hidden id="sender' + str(tk.id) + '">' + tk.sender.username + '</p><p>' + tk.sender.fullname + '</p>'
            note = r'<a data-toggle="modal" data-target="#all_note" data-title="new" id="' + str(tk.id)+'"><i class="fa fa-pencil-square-o"></i></a>'
            # if tk.expired == 1:
            #     status += r'<br><span class ="label label-danger"> Quá hạn </span>'
            dateend = tk.dateend + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.id) + '">'+ str(tk.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            data.append([idtk, tk.loai_su_co, service, status, note, downtime, sender, handler, dateend, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def home_chart(request):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        leader = Agents.objects.get(username=request.session['leader'])
        content = {
            'today': timezone.now().date(),
            'agent_name': mark_safe(json.dumps(leader.username)),
            'fullname': mark_safe(json.dumps(leader.fullname)),
            'leader': leader,
        }
        if Agents.objects.get(username=request.session['leader']).position == 2:
            try:
                service = Services.objects.filter(leader=leader)
            except ObjectDoesNotExist:
                pass
            else:
                content['service'] = service
                content['1_service'] = service[0]

        else:
            try:
                service = Services.objects.filter(leader_bk=leader)
            except ObjectDoesNotExist:
                pass
            else:
                content['service'] = service
                content['1_service'] = service[0]

        return render(request, 'leader/chart.html', content)
    else:
        return redirect("/")


def data_line_year(request, year, service):
    sv = Services.objects.get(name=service)
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    labels = []
    data = []
    if year == year_now:
        for i in range(1, month_now+1):
            labels.append('Tháng ' + str(i))
            data.append(Tickets.objects.filter(serviceid=sv, date_close__year=year, date_close__month=i, status=3).count())
    elif year < year_now:
        for i in range(1, 13):
            labels.append('Tháng ' + str(i))
            data.append(Tickets.objects.filter(serviceid=sv, date_close__year=year, date_close__month=i, status=3).count())
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


def data_line_month(request, month, year, service):
    sv = Services.objects.get(name=service)
    day_now = int(timezone.now().day)
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    labels = []
    data = []
    if year == year_now:
        if month == month_now:
            for i in range(1, day_now+1):
                labels.append('Ngày ' + str(i))
                data.append(Tickets.objects.filter(date_close__year=year, date_close__month=month, date_close__day=i,
                                                   status=3, serviceid=sv).count())
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
                                                   date_close__day=i, status=3, serviceid=sv).count())
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
                                               date_close__day=i, status=3, serviceid=sv).count())
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


def data_pie_year(request, year, service):
    sv = Services.objects.get(name=service)
    year_now = int(timezone.now().year)
    if year <= year_now:
        tk_dung_han = Tickets.objects.filter(expired=0, serviceid=sv, status=3, date_close__year=year)
        tk_sai_han = Tickets.objects.filter(expired=1, serviceid=sv, status=3, date_close__year=year)
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


def data_pie_month(request, month, year, service):
    sv = Services.objects.get(name=service)
    year_now = int(timezone.now().year)
    month_now = int(timezone.now().month)
    if year == year_now:
        if month <= month_now:
            tk_dung_han = Tickets.objects.filter(expired=0, serviceid=sv, status=3, date_close__year=year, date_close__month=month)
            tk_sai_han = Tickets.objects.filter(expired=1, serviceid=sv, status=3, date_close__year=year, date_close__month=month)
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
        tk_dung_han = Tickets.objects.filter(expired=0,serviceid=sv, status=3, date_close__year=year, date_close__month=month)
        tk_sai_han = Tickets.objects.filter(expired=1,serviceid=sv, status=3, date_close__year=year, date_close__month=month)
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


def leader_manage_agent(request):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        if Agents.objects.get(username=request.session['leader']).position == 2:
            if request.method == 'POST':
                if 'delete' in request.POST:
                    ss, tpid, agid = request.POST['delete'].split('_')
                    ServiceAgent.objects.get(serviceid=Services.objects.get(id=tpid), agentid=Agents.objects.get(id=agid)).delete()
                elif 'serviceid' in request.POST:
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    top = Services.objects.get(id=request.POST['serviceid'])
                    if not list_agent:
                            pass
                    else:
                        for agentname in list_agent:
                            try:
                                ag = Agents.objects.get(username=agentname)
                                ServiceAgent.objects.get(agentid=ag, serviceid=top)
                            except ObjectDoesNotExist:
                                ag = Agents.objects.get(username=agentname)
                                ServiceAgent.objects.create(agentid=ag, serviceid=top)
                elif 'svname' in request.POST:
                    try:
                        ag = Agents.objects.get(id=request.POST['agid'])
                        sv = Services.objects.get(name=request.POST['svname'])
                        if sv.leader_bk == None:
                            ag.position = 4
                            ag.save()
                            sv.leader_bk = ag
                            sv.save()
                        else:
                            if Services.objects.filter(leader_bk=ag).count() == 1:
                                ag.position = 1
                                ag.save()
                            sv.leader_bk = None
                            sv.save()
                    except:
                        pass

            leader = Agents.objects.get(username=request.session['leader'])
            list_topic = Services.objects.filter(leader=leader)
            list_ag = {}
            list_tk = {}
            for tp in list_topic:
                ag = ServiceAgent.objects.filter(serviceid=tp)
                list_ag[tp] = [a.agentid for a in ag]
            for ag in Agents.objects.all():
                list_tk[ag.username] = count_tk(ag.username)
            content = {'list_ag': list_ag,
                    'topic': list_topic,
                    'leng': len(list_topic),
                    'topic': list_topic,
                    'list_tk': list_tk,
                    'agent_name': mark_safe(json.dumps(leader.username)),
                    'fullname': mark_safe(json.dumps(leader.fullname)),
                    'leader': leader
                    }
            return render(request, 'leader/leader_manage_agent.html', content)
        else:
            if request.method == 'POST':
                if 'delete' in request.POST:
                    ss, tpid, agid = request.POST['delete'].split('_')
                    ServiceAgent.objects.get(serviceid=Services.objects.get(id=tpid), agentid=Agents.objects.get(id=agid)).delete()
                elif 'serviceid' in request.POST:
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    top = Services.objects.get(id=request.POST['serviceid'])
                    if not list_agent:
                            pass
                    else:
                        for agentname in list_agent:
                            try:
                                ag = Agents.objects.get(username=agentname)
                                ServiceAgent.objects.get(agentid=ag, serviceid=top)
                            except ObjectDoesNotExist:
                                ag = Agents.objects.get(username=agentname)
                                ServiceAgent.objects.create(agentid=ag, serviceid=top)
                elif 'svname' in request.POST:
                    try:
                        ag = Agents.objects.get(id=request.POST['agid'])
                        sv = Services.objects.get(name=request.POST['svname'])
                        if (ag.position != 4):
                            ag.position = 4
                            ag.save()
                            sv.leader_bk = ag
                            sv.save()
                        else:
                            ag.position = 1
                            ag.save()
                            sv.leader_bk = None
                            sv.save()
                    except:
                        pass

            leader = Agents.objects.get(username=request.session['leader'])
            list_topic = Services.objects.filter(leader_bk=leader)
            list_ag = {}
            list_tk = {}
            for tp in list_topic:
                ag = ServiceAgent.objects.filter(serviceid=tp)
                list_ag[tp] = [a.agentid for a in ag]
            for ag in Agents.objects.all():
                list_tk[ag.username] = count_tk(ag.username)
            content = {'list_ag': list_ag,
                    'topic': list_topic,
                    'leng': len(list_topic),
                    'topic': list_topic,
                    'list_tk': list_tk,
                    'agent_name': mark_safe(json.dumps(leader.username)),
                    'fullname': mark_safe(json.dumps(leader.fullname)),
                    'leader': leader
                    }
            return render(request, 'leader/leader_manage_agent.html', content)
    else:
        return redirect("/")


def leader_agent_data(request):
    if request.session.has_key('leader'):
        agent = Agents.objects.exclude(position__in=[2,3])
        list_agent = []
        for ag in agent:
            list_agent.append({"username": ag.username, "fullname": ag.fullname})
        return JsonResponse(list_agent, safe=False)
    else:
        return redirect('/')


def leader_profile(request):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        if Agents.objects.get(username=request.session['leader']).position == 2:
            agent = Agents.objects.get(username=request.session['leader'])
            topicag = Services.objects.filter(leader=agent)
            list_tp = ""
            for tp1 in topicag:
                list_tp += str(tp1.name) + "!"
            if request.method == 'POST':
                if 'change_user' in request.POST:
                    u = Agents.objects.get(id=request.POST['agentid'])
                    fullname = request.POST['change_user']
                    email = request.POST['email']
                    phone = request.POST['phone']
                    receive_mail = request.POST['receive_mail']
                    u.fullname = fullname
                    u.email = email
                    u.phone = phone
                    u.receive_email = receive_mail
                    u.save()
                elif 'pwd' in request.POST:
                    u = Agents.objects.get(id=request.POST['agentid'])
                    u.password = request.POST['pwd']
                    u.save()
                elif 'noti_noti' in request.POST:
                    agent.noti_noti = 0
                    agent.save()
                elif 'noti_chat' in request.POST:
                    agent.noti_chat = 0
                    agent.save()
            return render(request,"leader/profile_leader.html", {'agent': agent, 'noti_noti': agent.noti_noti,
                                                        'noti_chat': agent.noti_chat,
                                                        'topic': topicag,
                                                        'agent_name': mark_safe(json.dumps(agent.username)),
                                                        'fullname': mark_safe(json.dumps(agent.fullname)),
                                                        'list_tp': mark_safe(json.dumps(list_tp)),
                                                        'leader': agent})
        else:
            agent = Agents.objects.get(username=request.session['leader'])
            topicag = Services.objects.filter(leader_bk=agent)
            list_tp = ""
            for tp1 in topicag:
                list_tp += str(tp1.name) + "!"
            if request.method == 'POST':
                if 'change_user' in request.POST:
                    u = Agents.objects.get(id=request.POST['agentid'])
                    fullname = request.POST['change_user']
                    email = request.POST['email']
                    phone = request.POST['phone']
                    receive_mail = request.POST['receive_mail']
                    u.fullname = fullname
                    u.email = email
                    u.phone = phone
                    u.receive_email = receive_mail
                    u.save()
                elif 'pwd' in request.POST:
                    u = Agents.objects.get(id=request.POST['agentid'])
                    u.password = request.POST['pwd']
                    u.save()
                elif 'noti_noti' in request.POST:
                    agent.noti_noti = 0
                    agent.save()
                elif 'noti_chat' in request.POST:
                    agent.noti_chat = 0
                    agent.save()
            return render(request,"leader/profile_leader.html", {'agent': agent, 'noti_noti': agent.noti_noti,
                                                        'noti_chat': agent.noti_chat,
                                                        'topic': topicag,
                                                        'agent_name': mark_safe(json.dumps(agent.username)),
                                                        'fullname': mark_safe(json.dumps(agent.fullname)),
                                                        'list_tp': mark_safe(json.dumps(list_tp)),
                                                        'leader': agent})
    else:
        return redirect("/")


def leader_to_agent(request):
    if request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        request.session['agent'] = request.session['leader']
        del request.session['leader']
        return redirect('/agent')
    else:
        return redirect("/")
