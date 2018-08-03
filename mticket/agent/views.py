from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
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
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits


def home_agent(request):
    if request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session.get('agent'))
        svag = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        service = Services.objects.filter(id__in=svag)
        list_leader = [sv.leader for sv in service]
        process = Tickets.objects.filter(serviceid__in=service, status__in=[1, 2])
        done = Tickets.objects.filter(status=3, serviceid__in=service)
        tk_open = Tickets.objects.filter(status=0, serviceid__in=service).count()
        tk_processing = TicketAgent.objects.filter(agentid=agent, ticketid__in=process).count()
        tk_done = TicketAgent.objects.filter(agentid=agent, ticketid__in=done).count()
        tp = ServiceAgent.objects.filter(agentid=agent)
        list_tp = ""
        for tp in tp:
            list_tp += str(tp.serviceid.name) + "!"
        content = {
                    'agent': agent,
                    'agent_name': mark_safe(json.dumps(agent.username)),
                    'fullname': mark_safe(json.dumps(agent.fullname)),
                    'service_total': service.count(),
                    'tk_open': tk_open,
                    'tk_processing': tk_processing,
                    'tk_done': tk_done,
                    'noti_noti': agent.noti_noti,
                    'noti_chat': agent.noti_chat,
                    'list_tp': mark_safe(json.dumps(list_tp)),
                    'list_leader': list_leader,
                    'admin': agent.position,
                   }
        if request.method == 'POST':
            if 'tkid' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                ticket.status = 1
                ticket.save()
                TicketLog.objects.create(agentid=agent, ticketid=ticket, action='nhận xử lý yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                TicketAgent.objects.create(agentid=agent, ticketid=ticket)
                user = Agents.objects.get(id=ticket.sender.id)
                if user.receive_email == 1:
                    email = EmailMessage(
                        'nhận xử lý yêu cầu',
                        render_to_string('agent/mail/assign_mail.html',
                                         {'receiver': user,
                                          'domain': (get_current_site(request)).domain,
                                          'sender': agent,
                                          'ticketid': ticket.id}),
                        to=[user.email],
                    )
                    thread = EmailThread(email)
                    thread.start()
            if 'noti_noti' in request.POST:
                agent.noti_noti = 0
                agent.save()
            if 'noti_chat' in request.POST:
                agent.noti_chat = 0
                agent.save()
        return render(request, 'agent/home_agent.html', content)
    else:
        return redirect("/")


def home_agent_data(request):
    if request.session.has_key('agent') and (Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session.get('agent'))
        svag = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        service = Services.objects.filter(id__in=svag)
        data = []
        for tk in Tickets.objects.filter(status=0, serviceid__in=service).order_by('-id'):
            client = r'<a data-toggle="collapse" data-target="#client' + str(tk.id)+'">' + tk.client + '   <i class="fa fa-plus-circle"></i></a><br><div id="client' + str(tk.id)+'" class="collapse">' + tk.info_client+'</div>'
            content = r'<a data-toggle="collapse" data-target="#content' + str(tk.id)+'">' + str(tk.content[:16])+ '   <i class="fa fa-plus-circle"></i></a><br><div id="content' + str(tk.id)+'" class="collapse">' + tk.content+'</div>'
            if tk.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.id)+'"></a>'
            else:
                attach = ''
            datestart = r'<p>'+ str(tk.datestart + timezone.timedelta(hours=7))[:-16] +'</p>'
            dateend = r'<p id="dateend' + str(tk.id) + '">'+ str(tk.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            downtime = '''<p class="downtime" id="downtime-''' + str(tk.id) + '''"></p>'''
            if tk.status == 0:
                status = r'<span class ="label label-danger"> Chờ</span>'
            elif tk.status == 1:
                status = r'<span class ="label label-warning"> Đang xử lý </span>'
            elif tk.status == 2:
                status = r'<span class ="label label-success"> Hoàn thành </span>'
            else:
                status = r'<span class ="label label-default"> Đóng </span>'
            option = '<button type="button" class="btn btn-success assign_ticket" id="' + str(tk.id) + '">Nhận</button><input id="user_name'+str(tk.id)+'" type="hidden" value="'+ tk.sender.username+'">'
            data.append([tk.id, client, tk.serviceid.name, tk.loai_su_co, content, tk.thong_so_kt,
                         attach, datestart, dateend, downtime, status, tk.sender.fullname, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def logout(request):
    del request.session['agent']
    return redirect("/")


def processing_ticket(request):
    if request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        sender = Agents.objects.get(username=request.session['agent'])
        admin = sender.position
        agent = Agents.objects.exclude(Q(username=request.session['agent']) | Q(position__in=[0, 2, 3]))
        tpag = ServiceAgent.objects.filter(agentid=sender).values('serviceid')
        sv = Services.objects.filter(id__in=tpag)
        idleader = Services.objects.filter(id__in=tpag).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        list_ag = {}
        for t in sv:
            ag = ServiceAgent.objects.filter(serviceid=t, agentid__in=agent)
            list_ag[t.name] = [a.agentid for a in ag]
        form = ForwardForm()
        form1 = AddForm()
        tksd = TicketAgent.objects.filter(agentid=sender)
        tksdpr = Tickets.objects.filter(id__in=tksd.values('ticketid'), status__in=[1, 2])
        service = ServiceAgent.objects.filter(agentid=sender)
        list_tp = ""
        for tp1 in service:
            list_tp += str(tp1.serviceid.name) + "!"
        content = {'list_ag': list_ag,
                   'service': sv,
                   'noti_noti': sender.noti_noti,
                   'noti_chat': sender.noti_chat,
                   'agent': agent, 'ticket': tksdpr,
                   'form': form,
                   'form1': form1,
                   'agent_name': mark_safe(json.dumps(sender.username)),
                   'fullname': mark_safe(json.dumps(sender.fullname)),
                   'list_tp': mark_safe(json.dumps(list_tp)),
                   'list_leader': list_leader,
                   'admin': admin}
        if request.method == 'POST':
            if 'noti_noti' in request.POST:
                sender.noti_noti = 0
                sender.save()
            elif 'noti_chat' in request.POST:
                sender.noti_chat = 0
                sender.save()
            elif 'type' in request.POST:
                if request.POST['type'] == 'forward_agent':
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    tk = Tickets.objects.get(id=request.POST['ticketid'])
                    receiver = Agents.objects.filter(username__in=list_agent)
                    text = request.POST['content']
                    for rc in receiver:
                        if rc != sender:
                            try:
                                TicketAgent.objects.get(ticketid=tk, agentid=rc)
                            except ObjectDoesNotExist:
                                try:
                                    ForwardTickets.objects.get(senderid=sender, receiverid=rc, ticketid=tk)
                                except ObjectDoesNotExist:
                                    ForwardTickets.objects.create(senderid=sender, receiverid=rc, ticketid=tk,content=text)
                                    if rc.receive_email == 1:
                                        email = EmailMessage(
                                            'Chuyển yêu cầu',
                                            render_to_string('agent/mail/forward_mail.html',
                                                            {'receiver': rc,
                                                            # 'domain': "113.190.232.90:8892",
                                                            'domain': (get_current_site(request)).domain,
                                                            'sender': sender}),
                                            to=[rc.email],
                                        )
                                        thread = EmailThread(email)
                                        thread.start()
                    return redirect("/agent/processing_ticket")
                elif request.POST['type'] == 'add_agent':
                    list_agent = request.POST['list_agent[]']
                    list_agent = json.loads(list_agent)
                    tk = Tickets.objects.get(id=request.POST['ticketid'])
                    receiver = Agents.objects.filter(username__in=list_agent)
                    text = request.POST['content']
                    for rc in receiver:
                        if rc != sender:
                            try:
                                TicketAgent.objects.get(ticketid=tk,agentid=rc)
                            except ObjectDoesNotExist:
                                try:
                                    AddAgents.objects.get(senderid=sender, receiverid=rc, ticketid=tk)
                                except ObjectDoesNotExist:
                                    AddAgents.objects.create(senderid=sender, receiverid=rc, ticketid=tk, content=text)
                                    if rc.receive_email == 1:
                                        email = EmailMessage(
                                            'Thêm vào xử lý yêu cầu',
                                            render_to_string('agent/mail/add_mail.html',
                                                            {'receiver': rc,
                                                            'domain': "113.190.232.90:8892",
                                                            # 'domain': (get_current_site(request)).domain,
                                                            'sender': sender}),
                                            to=[rc.email]
                                        )
                                        thread = EmailThread(email)
                                        thread.start()
                    return redirect("/agent/processing_ticket")
                elif request.POST['type'] == 'process_done':
                    tkid = request.POST['tkid']
                    stt = request.POST['stt']
                    ticket = Tickets.objects.get(id=tkid)
                    ticket.status = stt
                    ticket.save()
                    action =''
                    if stt == '1':
                        action += 'xử lý lại yêu cầu'
                    else:
                        action += 'xử lý xong yêu cầu'
                        ticket.note = request.POST['comment']
                        ticket.save()
                        user = Agents.objects.get(id=ticket.sender.id)
                        if user.receive_email == 1:
                            email = EmailMessage(
                                'Yêu cầu đã xử lý xong',
                                render_to_string('agent/mail/done_mail.html',
                                                {'receiver': user,
                                                'domain': (get_current_site(request)).domain,
                                                'sender': sender,
                                                'ticketid': ticket.id}),
                                to=[user.email],
                            )
                            thread = EmailThread(email)
                            thread.start()
                    TicketLog.objects.create(agentid=sender, ticketid=ticket,
                                            action=action,
                                            date=timezone.now().date(),
                                            time=timezone.now().time())
                elif request.POST['type'] == 'give_up':
                    ticket = Tickets.objects.get(id=request.POST['tkid'])
                    try:
                        TicketAgent.objects.get(ticketid=ticket)
                    except MultipleObjectsReturned:
                        tk = TicketAgent.objects.get(ticketid=ticket, agentid=sender)
                        tk.delete()
                        TicketLog.objects.create(agentid=sender, ticketid=ticket, action='từ bỏ xử lý yêu cầu',
                                                date=timezone.now().date(),
                                                time=timezone.now().time())
        return render(request, 'agent/processing_ticket.html', content)
    else:
        return redirect("/")


def processing_ticket_data(request):
    if request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session['agent'])
        tksd = TicketAgent.objects.filter(agentid=agent)
        tksdpr = Tickets.objects.filter(id__in=tksd.values('ticketid'), status__in=[1, 2])
        data = []
        for tk in tksdpr:
            # client = r'<a data-toggle="collapse" data-target="#client' + str(tk.id)+'">' + tk.client + '</a><br><div id="client' + str(tk.id)+'" class="collapse">' + tk.info_client+'</div>'
            content = r'<a data-toggle="collapse" data-target="#content' + str(tk.id)+'">' + str(tk.content[:16])+ '   <i class="fa fa-plus-circle"></i></a><br><div id="content' + str(tk.id)+'" class="collapse">' + tk.content+'</div>'
            if tk.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.id)+'"></a>'
            else:
                attach = ''
            option = '<div class="btn-group">'
            if tk.status == 1:
                status = r'<span class ="label label-warning" > Đang xử lý</span>'
                option += r'''<button id="''' + str(tk.id) + '''" type="button" class="btn btn-success handle_done" data-toggle="modal" data-title="done" data-target="#note"><i data-toggle="tooltip" title="Hoàn thành" class="fa fa-check"></i></button>'''
            else:
                status = r'<span class ="label label-success" > Hoàn thành</span>'
                option += r'''<button id="''' + str(tk.id) + '''" type="button" class="btn btn-success handle_processing"><i data-toggle="tooltip" title="Xử lý" class="fa fa-wrench"></i></button>'''
            handler = '<p hidden id="hd' + str(tk.id) + '">'
            service = '<p id="tp' + str(tk.id) + '">' + tk.serviceid.name + '</p>'
            tem = 0
            tkag = TicketAgent.objects.filter(ticketid=tk.id)
            for t in tkag:
                tem += 1
                handler += t.agentid.username + "<br>"
            handler += '</p>'
            for t in tkag:
                handler += t.agentid.fullname + '<br>'
            downtime = '''<span class="downtime label label-danger" id="downtime-'''+str(tk.id)+'''"></span>'''
            datestart = tk.datestart + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.id) + '">' + str(tk.dateend + timezone.timedelta(hours=7))[:-16] + '</p>'
            option += r'''<input type="hidden" id="user''' + str(tk.id) + '''" value="'''+tk.sender.username+'''">
            <a href='javascript:register_popup_agent("chat''' + str(tk.id) + '''", ''' + str(tk.id) + ''', "'''+tk.sender.fullname+'''", "'''+tk.sender.username+'''");' type="button" class="btn btn-primary" data-toggle="tooltip" title="Trò chuyện" id="chat_with_user"><i class="fa fa-commenting"></i><input type="hidden" value="''' + str(tk.id) + '''"/></a>
            <button id="''' + str(tk.id) + '''" type="button" class="btn btn-info fw_agent" data-toggle="modal" data-title="forward" data-target="#forward_add"><i class="fa fa-share-square-o" data-toggle="tooltip" title="Chuyển tiếp" ></i></button></div><br><div class="btn-group">
            <button id="''' + str(tk.id) + '''" type="button" class="btn btn-info add_agent" data-toggle="modal" data-title="add" data-target="#forward_add"><i class="fa fa-user-plus" data-toggle="tooltip" title="Thêm nhân viên" ></i></button></div>'''
            if tem == 1:
                option += r'''<button id="''' + str(tk.id) + '''" disabled type="button" class="btn btn-danger give_up" data-toggle="tooltip" title="Từ bỏ" ><i class="fa fa-minus-circle"></i></button>'''
            else:
                option += r'''<button id="''' + str(tk.id) + '''" type="button" class="btn btn-danger give_up" data-toggle="tooltip" title="Từ bỏ" ><i class="fa fa-minus-circle"></i></button>'''
            option +='''<a target="_blank" href="/agent/history/'''+str(tk.id)+ '''" type="button" class="btn btn-warning" data-toggle="tooltip" title="Dòng thời gian" ><span class="glyphicon glyphicon-floppy-disk" ></span><i class="fa fa-history"></i></a>'''
            if tk.note != '':
                note = r'<a data-toggle="collapse" data-target="#note'+ str(tk.id)+'"><i class="fa fa-plus-circle"></i></a><br><div id="note' + str(tk.id)+'" class="collapse">' + tk.note+'</div>'
            else:
                note = ''
            data.append([tk.id, tk.sender.fullname, service, tk.loai_su_co, content, tk.thong_so_kt,note,
                         attach, str(datestart)[:-16], dateend, downtime, status, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def history(request,id):
    if (request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1):
        tems = TicketLog.objects.filter(ticketid=id)
        result = []
        for tem in tems:
            if tem.agentid.position == 0:
                action = "<b>Người dùng "
            elif tem.agentid.position == 1:
                action = "<b>Nhân viên "
            elif tem.agentid.position == 2:
                action = "<b>Quản trị "
            else:
                action = "<b>Quyền quản trị "
            action += str(tem.agentid.fullname) + "</b><br/>" + tem.action
            if tem.action == 'tạo mới yêu cầu':
                cont = "<i class='fa fa-plus' ></i>"
            elif tem.action == 'tạo mới và tự xử lý yêu cầu':
                cont = "<i class='fa fa-tag' ></i>"
            elif tem.action == 'gửi yêu cầu':
                cont = "<i class='fa fa-share-square' ></i>"
            elif tem.action == 'đóng yêu cầu':
                cont = "<i class='fa fa-power-off' ></i>"
            elif tem.action == 'nhận xử lý yêu cầu':
                cont = "<i class='fa fa-thumb-tack' ></i>"
            elif tem.action == 'xử lý xong yêu cầu':
                cont = "<i class='fa fa-check' ></i>"
            elif tem.action == 'xử lý lại yêu cầu':
                cont = "<i class='fa fa-refresh' ></i>"
            elif tem.action == 'mở lại yêu cầu':
                cont = "<i class='fa fa-repeat' ></i>"
            elif tem.action == 'từ bỏ xử lý yêu cầu':
                cont = "<i class='fa fa-sign-out' ></i>"
            else:
                cont = "<i class='fa fa-user-secret' ></i>"
            result.append({"id": tem.id,
                           "title": action,
                           "content": cont,
                           "group": "period",
                           "start": str(tem.date)+"T"+str(tem.time)[:-7]})
        maxtime = TicketLog.objects.filter(ticketid=id).latest('id')
        mintime = TicketLog.objects.filter(ticketid=id).earliest('id')
        if maxtime.ticketid.status == 0:
            status = '<font color="red"> chờ </font>'
        elif maxtime.ticketid.status == 1:
            status = '<font color="orange"> đang xử lý </font>'
        elif maxtime.ticketid.status == 2:
            status = '<font color="green"> hoàn thành </font>'
        else:
            status = '<font color="gray"> đóng </font>'
        tim = str(timezone.datetime.combine(maxtime.date, maxtime.time) - timezone.datetime.combine(
            mintime.date, mintime.time))[:-7]
        result.append({"id": 0,
                       "content": "Yêu cầu số "+str(id)+" " + status + " (thời gian tồn tại " + tim + ")",
                       "type": "point",
                       "group": "overview",
                       "start": str(mintime.date) + "T" + str(mintime.time)[:-7]})
        tk = json.loads(json.dumps(result))
        agent = Agents.objects.get(username=request.session['agent'])
        tpag = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        idleader = Services.objects.filter(id__in=tpag).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        return render(request, 'agent/history_for_agent.html', {'tk': tk, 'id': str(id), 'list_leader': list_leader})
    else:
        return redirect("/")


def inbox(request):
    if request.session.has_key('agent') and (Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session.get('agent'))
        admin = agent.position
        svag = ServiceAgent.objects.filter(agentid=agent)
        svag1 = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        idleader = Services.objects.filter(id__in=svag1).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        list_tp = ""
        for tp1 in svag:
            list_tp += str(tp1.serviceid.name) + "!"
        content = {'forwardin': ForwardTickets.objects.filter(receiverid=agent),
                   'noti_noti': agent.noti_noti,
                   'noti_chat': agent.noti_chat,
                   'addin': AddAgents.objects.filter(receiverid=agent),
                   'agent_name': mark_safe(json.dumps(agent.username)),
                   'fullname': mark_safe(json.dumps(agent.fullname)),
                   'list_tp': mark_safe(json.dumps(list_tp)),
                   'list_leader': list_leader,
                   'admin': admin}
        if request.method == 'POST':

            if 'forward' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                try:
                    addagent = AddAgents.objects.get(ticketid=ticket, receiverid=agent)
                except ObjectDoesNotExist:
                    pass
                else:
                    addagent.delete()
                fwticket = ForwardTickets.objects.get(ticketid=ticket, receiverid=agent)
                sender = fwticket.senderid
                agticket = TicketAgent.objects.get(ticketid=ticket, agentid=fwticket.senderid)
                fwticket.delete()
                if 'agree' not in request.POST:
                    if sender.receive_email == 1:
                        email = EmailMessage(
                            'Từ chối nhận xử lý yêu cầu',
                            render_to_string('agent/mail/deny_mail.html',
                                             {'receiver': sender,
                                              # 'domain': "113.190.232.90:8892",
                                              'domain': (get_current_site(request)).domain,
                                              'sender': agent}),
                            to=[sender.email]
                        )
                        thread = EmailThread(email)
                        thread.start()
                else:
                    try:
                        TicketAgent.objects.get(ticketid=ticket, agentid=agent)
                    except TicketAgent.DoesNotExist:
                        agticket.agentid = agent
                        agticket.save()
                        action = "nhận xử lý yêu cầu được gửi bởi nhân viên " + sender.username
                        TicketLog.objects.create(agentid=agent, ticketid=ticket, action=action,
                                                 date=timezone.now().date(),
                                                 time=timezone.now().time())
                        if sender.receive_email == 1:
                            email = EmailMessage(
                                'Chấp nhận yêu cầu chuyển đến',
                                render_to_string('agent/mail/accept_mail.html',
                                                 {'receiver': sender,
                                                  # 'domain': "113.190.232.90:8892",
                                                  'domain': (get_current_site(request)).domain,
                                                  'sender': agent}),
                                to=[sender.email]
                            )
                            thread = EmailThread(email)
                            thread.start()
                    else:
                        agticket.delete()
            elif 'add' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                try:
                    fwticket = ForwardTickets.objects.get(ticketid=ticket, receiverid=agent)
                except ObjectDoesNotExist:
                    pass
                else:
                    fwticket.delete()
                addagent = AddAgents.objects.get(ticketid=ticket, receiverid=agent)
                sender = addagent.senderid
                addagent.delete()
                if 'agree' not in request.POST:
                    if sender.receive_email == 1:
                        email = EmailMessage(
                            'Từ chối',
                            render_to_string('agent/mail/deny_mail.html',
                                             {'receiver': sender,
                                              # 'domain': "113.190.232.90:8892",
                                                'domain': (get_current_site(request)).domain,
                                              'sender': agent}),
                            to=[sender.email]
                        )
                        thread = EmailThread(email)
                        thread.start()
                else:
                    try:
                        TicketAgent.objects.get(ticketid=ticket, agentid=agent)
                    except TicketAgent.DoesNotExist:
                        TicketAgent.objects.create(ticketid=ticket, agentid=agent)
                        action = 'tham gia xử lý yêu cầu'
                        TicketLog.objects.create(agentid=agent, ticketid=ticket, action=action,
                                                 date=timezone.now().date(),
                                                 time=timezone.now().time())
                        if sender.receive_email == 1:
                            email = EmailMessage(
                                'Chấp nhận yêu cầu',
                                render_to_string('agent/mail/accept_mail.html',
                                                 {'receiver': sender,
                                                  # 'domain': "113.190.232.90:8892",
                                                    'domain': (get_current_site(request)).domain,
                                                  'sender': agent}),
                                to=[sender.email]
                            )
                            thread = EmailThread(email)
                            thread.start()
            elif 'noti_noti' in request.POST:
                agent.noti_noti = 0
                agent.save()
            elif 'noti_chat' in request.POST:
                agent.noti_chat = 0
                agent.save()
        return render(request, 'agent/inbox.html', content)
    else:
        return redirect("/")


def outbox(request):
    if request.session.has_key('agent') and (Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session.get('agent'))
        admin = agent.position
        svag = ServiceAgent.objects.filter(agentid=agent)
        svag1 = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        idleader = Services.objects.filter(id__in=svag1).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        list_tp = ""
        for tp1 in svag:
            list_tp += str(tp1.serviceid.name) + "!"
        content = {'forwardout': ForwardTickets.objects.filter(senderid=agent),
                   'noti_noti': agent.noti_noti,
                   'noti_chat': agent.noti_chat,
                   'addout': AddAgents.objects.filter(senderid=agent),
                   'agent_name': mark_safe(json.dumps(agent.username)),
                   'fullname': mark_safe(json.dumps(agent.fullname)),
                   'list_tp': mark_safe(json.dumps(list_tp)),
                   'list_leader': list_leader,
                   'admin': admin}
        if request.method == 'POST':
            if 'forward' in request.POST:
                fwticket = ForwardTickets.objects.get(id=request.POST['tkid'])
                fwticket.delete()
            elif 'add' in request.POST:
                fwticket = AddAgents.objects.get(id=request.POST['tkid'])
                fwticket.delete()
            elif 'noti_noti' in request.POST:
                agent.noti_noti = 0
                agent.save()
            elif 'noti_chat' in request.POST:
                agent.noti_chat = 0
                agent.save()

        return render(request, 'agent/outbox.html', content)
    else:
        return redirect("/")


def profile(request):
    if request.session.has_key('agent') and (Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session['agent'])
        admin = agent.position
        tpag1 = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        idleader = Services.objects.filter(id__in=tpag1).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        topicag = ServiceAgent.objects.filter(agentid=agent)
        list_tp = ""
        for tp1 in topicag:
            list_tp += str(tp1.serviceid.name) + "!"
        tpag = [ta.serviceid.name for ta in ServiceAgent.objects.filter(agentid=agent)]
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
        return render(request, "agent/profile.html", {'agent': agent, 'noti_noti': agent.noti_noti,
                                                      'noti_chat': agent.noti_chat,
                                                      'topic': tpag,
                                                      'agent_name': mark_safe(json.dumps(agent.username)),
                                                      'fullname': mark_safe(json.dumps(agent.fullname)),
                                                      'list_tp': mark_safe(json.dumps(list_tp)),
                                                      'list_leader': list_leader,
                                                      'admin': admin})
    else:
        return redirect("/")


def closed_ticket(request):
    if request.session.has_key('agent') and (Agents.objects.get(username=request.session['agent'])).status == 1:
        agent = Agents.objects.get(username=request.session['agent'])
        admin = agent.position
        tpag1 = ServiceAgent.objects.filter(agentid=agent).values('serviceid')
        idleader = Services.objects.filter(id__in=tpag1).values('leader')
        list_leader = Agents.objects.filter(id__in=idleader)
        tem = Tickets.objects.filter(status=3)
        topicag = ServiceAgent.objects.filter(agentid=agent)
        list_tp = ""
        for tp1 in topicag:
            list_tp += str(tp1.serviceid.name) + "!"
        content = {'noti_noti': agent.noti_noti,
                   'noti_chat': agent.noti_chat,
                   'ticket': TicketAgent.objects.filter(agentid=agent, ticketid__in=tem),
                   'agent_name': mark_safe(json.dumps(agent.username)),
                   'fullname': mark_safe(json.dumps(agent.fullname)),
                   'list_tp': mark_safe(json.dumps(list_tp)),
                   'list_leader': list_leader,
                   'admin': admin}
        if request.method == 'POST':
            if 'noti_noti' in request.POST:
                agent.noti_noti = 0
                agent.save()
            elif 'noti_chat' in request.POST:
                agent.noti_chat = 0
                agent.save()
        return render(request, 'agent/closed_ticket.html', content)
    else:
        return redirect("/")


def agent_to_leader(request):
    if request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        request.session['leader'] = request.session['agent']
        del request.session['agent']
        return redirect('/leader')
    else:
        return redirect("/")