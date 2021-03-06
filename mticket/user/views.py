from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from django.conf import settings
import threading
import json
from .forms import *
import string
import datetime
from random import *
from django.contrib.auth.decorators import login_required
min_char = 8
max_char = 12
allchar = string.ascii_letters + string.digits

MAX_UPLOAD_SIZE = 2097152


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()


def login_user(request):
    mess_resetpwd_error = 'Email chưa đăng ký hoặc không hợp lệ'
    mess_resetpwd_ok = 'Hãy kiểm tra email của bạn để cập nhật lại mật khẩu'
    mess_register_error = 'Thông tin đăng ký không hợp lý'
    mess_register_ok = 'Hãy kiểm tra email của bạn để hoàn tất đăng ký'
    mess_login_error = 'Đăng nhập thất bại'
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        return redirect("/user")
    elif request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        return redirect('/agent')
    elif request.session.has_key('admin')and(Agents.objects.get(username=request.session['admin'])).status == 1:
        return redirect('/admin')
    elif request.session.has_key('leader')and(Agents.objects.get(username=request.session['leader'])).status == 1:
        return redirect('/leader')
    else:
        if request.method == 'POST':
            # post form để User yêu cầu reset mật khẩu, gửi link về mail
            if 'uemail' in request.POST:
                form = UserResetForm(request.POST)
                if form.is_valid():
                    to_email = form.cleaned_data['uemail']
                    current_site = get_current_site(request)
                    user = get_user_email(to_email)
                    mail_subject = 'Reset password your account.'
                    message = render_to_string('user/resetpwd.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_error, 'error': error})
            # Post form User đăng kí tài khoản, gửi link xác nhận về mail
            elif 'fullname' and 'email' and 'password2' in request.POST:
                form = RegistrationForm(request.POST)
                if form.is_valid():
                    current_site = get_current_site(request)
                    user = form.save()

                    mail_subject = 'Activate your blog account.'
                    message = render_to_string('user/acc_active_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data['email']
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html',{'mess': mess_register_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html',{'mess': mess_register_error,'error':error})
            # Agent đăng nhập, nếu là agent thường thì login bình thường, Maser-admin thì cần code xác thực
            elif 'agentname' and 'agentpass' in request.POST:
                form = AgentLoginForm(request.POST)
                if form.is_valid():
                    agentname = form.cleaned_data['agentname']
                    agentpass = form.cleaned_data['agentpass']
                    if authenticate_agent(agentname=agentname, agentpass=agentpass) is None:
                        return render(request, 'user/index.html', {'mess': mess_login_error})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 0:
                        ag = get_agent(agentname)
                        if ag.status == 1:
                            request.session['user'] = agentname
                            return redirect('/user')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 1:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['agent'] = agentname
                            return redirect('/agent')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 2:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['leader'] = agentname
                            return redirect('/leader')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 3:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['admin'] = agentname
                            return redirect('/admin')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 4:
                        ag = Agents.objects.get(username=agentname)
                        if ag.status == 1:
                            request.session['leader'] = agentname
                            return redirect('/leader')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_login_error,'error':error})
        return render(request, 'user/index.html', {})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Agents.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Agents.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.status = 1
        user.save()
        return redirect('/')
    else:
        return HttpResponse('Đường dẫn không hợp lệ!')


def logout_user(request):
    del request.session['user']
    return redirect("/")


def homeuser(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        # admin = Agents.objects.get(admin=1)
        form = CreateNewTicketForm()
        group = GroupServices.objects.all()
        ls_group = {}
        for gr in group:
            ls_group[gr.name] = Services.objects.filter(groupserviceid=gr)
        service = Services.objects.all()
        ticket = Tickets.objects.filter(sender=user.id).order_by('-id')
        handler = TicketAgent.objects.all()
        content = {'ticket': ticket,
                   'form': form,
                   'user': user,
                   'group': ls_group,
                   'handler': handler,
                   'service': service,
                   'username': mark_safe(json.dumps(user.username)),
                   'fullname': mark_safe(json.dumps(user.fullname)),
                   # 'admin': mark_safe(json.dumps(admin.username)),
                   'noti_noti': user.noti_noti,
                   'noti_chat': user.noti_chat,
                   }
        if request.method == 'POST':
            if 'tkid' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                ticket.status = 3
                ticket.date_close = timezone.now()
                ticket.save()
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='đóng yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                try:
                    tkag = TicketAgent.objects.filter(ticketid=request.POST['tkid']).values('agentid')
                except ObjectDoesNotExist:
                    pass
                else:
                    receiver = Agents.objects.filter(id__in=tkag)
                    for rc in receiver:
                        if rc.receive_email == 1:
                            email = EmailMessage('Đóng yêu cầu',
                                                 render_to_string('user/close_email.html',
                                                                  {'receiver': rc, 'sender': user, 'id': id}),
                                                 to=[rc.email], )
                            thread = EmailThread(email)
                            thread.start()
            elif 'tkid_send' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid_send'])
                ticket.status = 0
                ticket.save()
                TicketLog.objects.create(agentid=user,
                                         ticketid=ticket,
                                         action='gửi yêu cầu',
                                         date=timezone.now().date(),
                                         time=timezone.now().time())
                tkag = TicketAgent.objects.get(ticketid=ticket, agentid=user)
                tkag.delete()
            elif 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
            elif 'noti_chat' in request.POST:
                user.noti_chat = 0
                user.save()
            else:
                form = CreateNewTicketForm(request.POST, request.FILES)
                if form.is_valid():
                    ticket = Tickets()
                    ticket.client = form.cleaned_data['client']
                    ticket.info_client = form.cleaned_data['info_client']
                    ticket.loai_su_co = form.cleaned_data['loai_su_co']
                    ticket.thong_so_kt = form.cleaned_data['thong_so_kt']
                    service = Services.objects.get(name=request.POST['service'])
                    ticket.serviceid = service
                    ticket.lv_priority = int(request.POST['lv_priority'])
                    ticket.content = form.cleaned_data['content']
                    ticket.sender = user
                    ticket.datestart = timezone.now()
                    ticket.dateend = (timezone.now() + timezone.timedelta(minutes=service.downtime))
                    if request.FILES.get('attach') is not None:
                        if request.FILES['attach']._size < MAX_UPLOAD_SIZE:
                            ticket.attach = request.FILES['attach']
                            handle_uploaded_file(request.FILES['attach'])
                        else:
                            return render(request, 'user/home_user.html', content)
                    if request.POST['kind'] == 'tu_xu_ly':
                        ticket.status = 1
                        ticket.save()
                        TicketAgent.objects.create(agentid=user, ticketid=ticket)
                        action = 'tạo mới và tự xử lý yêu cầu'
                    else:
                        ticket.save()
                        action = 'tạo mới yêu cầu'
                    TicketLog.objects.create(agentid=user,
                                             ticketid=ticket,
                                             action=action,
                                             date=timezone.now().date(),
                                             time=timezone.now().time())
                return redirect("/user")
        return render(request, 'user/home_user.html', content)
    else:
        return redirect("/")


def handle_uploaded_file(f):
    # path = settings.MEDIA_ROOT+"/photos/"+f.name
    path = "media/photos/" + f.name
    file = open(path, 'wb+')
    for chunk in f.chunks():
        file.write(chunk)
    file.close()


def homeuser_data_tu_xu_ly(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        tks = Tickets.objects.filter(sender=user.id, status=1).order_by('-id')
        tks_txl = TicketAgent.objects.filter(ticketid__in=tks, agentid=user)
        data = []
        for tk in tks_txl:
            client = r'<a data-toggle="collapse" data-target="#client'+ str(tk.ticketid.id)+'">' + tk.ticketid.client + '   <i class="fa fa-plus-circle"></i></a><br><div id="client' + str(tk.ticketid.id)+'" class="collapse">' + tk.ticketid.info_client+'</div>'
            content = r'<a data-toggle="collapse" data-target="#content'+ str(tk.ticketid.id)+'">' + str(tk.ticketid.content[:16])+ '   <i class="fa fa-plus-circle"></i></a><br><div id="content' + str(tk.ticketid.id)+'" class="collapse">' + tk.ticketid.content+'</div>'
            if tk.ticketid.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.ticketid.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.ticketid.id)+'"></a>'
            else:
                attach = ''
            if tk.ticketid.note != '':
                note = r'<a data-toggle="collapse" data-target="#note'+ str(tk.ticketid.id)+'"><i class="fa fa-plus-circle"></i></a><br><div id="note' + str(tk.ticketid.id)+'" class="collapse">' + tk.ticketid.note+'</div>'
            else:
                note = ''
            option = '''<div class="btn-group"><button type="button" class="btn btn-danger close_ticket_txl" data-toggle="tooltip" title="đóng" id="''' + str(tk.ticketid.id) + '''" ><span class="glyphicon glyphicon-off"></span></button>'''
            option += '''<button type="button" class="btn btn-primary send_ticket" data-toggle="tooltip" title="gửi" id="''' + tk.ticketid.serviceid.name + '''!'''+  str(tk.ticketid.id) + '''" ><span class="glyphicon glyphicon-send"></span></button>'''
            option += '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.ticketid.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a></div>'''
            datestart = tk.ticketid.datestart + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.ticketid.id) + '">'+ str(tk.ticketid.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            downtime = '''<p class="downtime" id="downtime-''' + str(tk.ticketid.id) + '''"></p>'''
            status = r'<span class ="label label-warning"> Đang xử lý </span>'
            data.append([tk.ticketid.id, client, tk.ticketid.serviceid.name, tk.ticketid.loai_su_co, content,
                         tk.ticketid.thong_so_kt, note, attach, str(datestart)[:-16], dateend, downtime, status, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def homeuser_data_gui_di(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        tk_txl_id = TicketAgent.objects.filter(agentid=user).values('ticketid')
        tk_txl = Tickets.objects.exclude(id__in=tk_txl_id).values('id')
        tks = Tickets.objects.filter(id__in=tk_txl ,sender=user.id, status__in=[0, 1, 2]).order_by('-id')
        data = []
        for tk in tks:
            client = r'<a data-toggle="collapse" data-target="#client'+ str(tk.id)+'">' + tk.client + '   <i class="fa fa-plus-circle"></i></a><br><div id="client' + str(tk.id)+'" class="collapse">' + tk.info_client+'</div>'
            content = r'<a data-toggle="collapse" data-target="#content'+ str(tk.id)+'">' + str(tk.content[:16])+ '   <i class="fa fa-plus-circle"></i></a><br><div id="content' + str(tk.id)+'" class="collapse">' + tk.content+'</div>'
            if tk.attach != '':
                attach = r'<a class="fa fa-image" data-title="' + str(tk.attach) + '" data-toggle="modal" data-target="#image" id="' + str(tk.id)+'"></a>'
            else:
                attach = ''
            if tk.note != '':
                note = r'<a data-toggle="collapse" data-target="#note'+ str(tk.id)+'"><i class="fa fa-plus-circle"></i></a><br><div id="note' + str(tk.id)+'" class="collapse">' + tk.note+'</div>'
            else:
                note = ''
            datestart = tk.datestart + timezone.timedelta(hours=7)
            dateend = r'<p id="dateend' + str(tk.id) + '">'+ str(tk.dateend + timezone.timedelta(hours=7))[:-16] +'</p>'
            downtime = '''<p class="downtime" id="downtime-''' + str(tk.id) + '''"></p>'''
            if tk.status == 0:
                status = r'<span class ="label label-danger"> Chờ</span>'
                handler = '<p id="hd' + str(tk.id) + '">Không có ai</p>'
            else:
                if tk.status == 1:
                    status = r'<span class ="label label-warning"> Đang xử lý </span>'
                elif tk.status == 2:
                    status = r'<span class ="label label-success"> Hoàn thành </span>'
                else:
                    status = r'<span class ="label label-default"> Đóng </span>'
                handler = '<p>'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.fullname + "<br>"
                handler += '</p><p hidden id="hd' + str(tk.id) + '">'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.username + "<br>"
                handler += '</p>'
            option = ''
            if tk.status < 3:
                option += '''<button type="button" class="btn btn-danger close_ticket_gui_di" data-toggle="tooltip" title="đóng" id="'''+str(tk.id)+'''" ><span class="glyphicon glyphicon-off"></span></button>'''
            else:
                option += '''<button disabled type="button" class="btn btn-danger close_ticket_gui_di" data-toggle="tooltip" title="đóng" id="'''+str(tk.id)+'''"><span class="glyphicon glyphicon-off"></span></button>'''
            if 1 == tk.status or tk.status == 2:
                option += '''<a href='javascript:register_popup("chat'''+str(tk.id)+'''", '''+str(tk.id)+''');' type="button" class="btn btn-primary" data-toggle="tooltip" title="trò chuyện" id="chat_with_agent"><span class="glyphicon glyphicon-comment" ></span><input type="hidden" value="'''+str(tk.id)+'''"/></a>'''
            else:
                option += '''<a  type="button" disabled class="btn btn-primary not-active" data-toggle="tooltip" title="trò chuyện"><span class="glyphicon glyphicon-comment" ></span></a>'''
            option += '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a>'''
            data.append([tk.id, client, tk.serviceid.name, tk.loai_su_co, content, tk.thong_so_kt, note,
                         attach, str(datestart)[:-16], dateend, downtime, status, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def detail_user(request):
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        if request.method == 'POST':
            if 'change_user' in request.POST:
                u = Agents.objects.get(id=request.POST['userid'])
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
                u = Agents.objects.get(id=request.POST['userid'])
                u.password = request.POST['pwd']
                u.save()
            elif 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
            elif 'noti_chat' in request.POST:
                user.noti_chat = 0
                user.save()
        return render(request, 'user/detail_user.html', {'user': user,
                                                         'username': mark_safe(json.dumps(user.username)),
                                                         'fullname': mark_safe(json.dumps(user.fullname)),
                                                         'noti_noti': user.noti_noti,
                                                         'noti_chat': user.noti_chat})
    else:
        return redirect("/")


def closed_ticket(request):
    if request.session.has_key('user')and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        return render(request, 'user/closed_ticket.html', {'user': user,
                                                         'username': mark_safe(json.dumps(user.username)),
                                                         'fullname': mark_safe(json.dumps(user.fullname)),
                                                         'noti_noti': user.noti_noti,
                                                         'noti_chat': user.noti_chat})
    else:
        return redirect("/")


def closed_ticket_data(request):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
        user = Agents.objects.get(username=request.session['user'])
        tks = Tickets.objects.filter(sender=user.id,status=3).order_by('-id')
        data = []
        for tk in tks:
            client = r'<a data-toggle="collapse" data-target="#client'+ str(tk.id)+'">' + tk.client + '</a><br><div id="client' + str(tk.id)+'" class="collapse">' + tk.info_client+'</div>'
            content = r'<a data-toggle="collapse" data-target="#content'+ str(tk.id)+'">' + str(tk.content[:16])+ '...</a><br><div id="content' + str(tk.id)+'" class="collapse">' + tk.content+'</div>'
            if tk.expired == 1:
                overdue = r'<span class ="label label-danger"> Quá hạn </span>'
            else:
                overdue = r'<span class ="label label-success"> Đúng hạn </span>'
            handler = '<p id="hd' + str(tk.id) + '">'
            for t in TicketAgent.objects.filter(ticketid=tk.id):
                handler += t.agentid.username + "<br>"
            handler += '</p>'
            option = '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a>'''
            datestart = tk.datestart + timezone.timedelta(hours=7)
            dateclosed = str(datestart)[:-16]
            data.append([tk.id, client, tk.serviceid.name, tk.loai_su_co, content, str(datestart)[:-16],
                         dateclosed, overdue, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def history(request, id):
    if request.session.has_key('user') and (Agents.objects.get(username=request.session['user'])).status == 1:
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
                cont = "<span class='glyphicon glyphicon-plus' ></span>"
            elif tem.action == 'tạo mới và tự xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-tag' ></span>"
            elif tem.action == 'gửi yêu cầu':
                cont = "<span class='glyphicon glyphicon-send' ></span>"
            elif tem.action == 'đóng yêu yêu cầu':
                cont = "<span class='glyphicon glyphicon-off' ></span>"
            elif tem.action == 'nhận xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-pushpin' ></span>"
            elif tem.action == 'xử lý xong yêu cầu':
                cont = "<span class='glyphicon glyphicon-ok' ></span>"
            elif tem.action == 'xử lý lại yêu cầu':
                cont = "<span class='glyphicon glyphicon-refresh' ></span>"
            elif tem.action == 'mở lại yêu cầu':
                cont = "<span class='glyphicon glyphicon-repeat' ></span>"
            elif tem.action == 'từ bỏ xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-log-out' ></span>"
            elif tem.action == 'tham gia xử lý yêu cầu':
                cont = "<span class='glyphicon glyphicon-user' ></span>"
            else:
                cont = "<span class='glyphicon glyphicon-user' ></span>"
            result.append({"id": tem.id,
                           "title": action,
                           "content": cont,
                           "group": "period",
                           "start": str(tem.date)+"T"+str(tem.time)[:-7]})
        maxtime = TicketLog.objects.filter(ticketid=id).latest('id')
        mintime = TicketLog.objects.filter(ticketid=id).earliest('id')
        if maxtime.ticketid.status == 0:
            status = '<font color="red">chờ</font>'
        elif maxtime.ticketid.status == 1:
            status = '<font color="orange">đang xử lý</font>'
        elif maxtime.ticketid.status == 2:
            status = '<font color="green">hoàn thành</font>'
        else:
            status = '<font color="gray">đóng</font>'
        tim = str(timezone.datetime.combine(maxtime.date, maxtime.time) - timezone.datetime.combine(
            mintime.date, mintime.time))[:-7]
        result.append({"id": 0,
                       "content": "Yêu cầu số " + str(id) + ": " + status + " (thời gian tồn tại " + tim + ")",
                       "type": "point",
                       "group": "overview",
                       "start": str(mintime.date) + "T" + str(mintime.time)[:-7]})
        tk = json.loads(json.dumps(result))
        return render(request, 'user/history.html', {'tk': tk, 'id': str(id)})
    else:
        return redirect("/")
