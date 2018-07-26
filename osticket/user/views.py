from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token, account_activation_token1
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

MAX_UPLOAD_SIZE = 10485760
dic = {}
dic_time = {}
Level_0 = 30
Level_1 = 20
Level_2 = 10


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()


def history(request, id):
    if request.session.has_key('user') and (Users.objects.get(username=request.session['user'])).status == 1:
        tems = TicketLog.objects.filter(ticketid=id)
        result = []
        for tem in tems:
            if tem.userid is not None:
                action = "<b>User " + str(tem.userid.username) + "</b><br/>" + tem.action
            else:
                action = "<b>Nhân viên " + str(tem.agentid.username) + "</b><br/>" + tem.action
            if tem.action == 'tạo mới yêu cầu':
                cont = "<span class='glyphicon glyphicon-plus' ></span>"
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


def homeuser(request):
    if request.session.has_key('user') and (Users.objects.get(username=request.session['user'])).status == 1:
        user = Users.objects.get(username=request.session['user'])
        admin = Agents.objects.get(admin=1)
        form = CreateNewTicketForm()
        topic = Topics.objects.filter().order_by('-id')
        ticket = Tickets.objects.filter(sender=user.id).order_by('-id')
        handler = TicketAgent.objects.all()
        level = LevelPriority.objects.all()
        content = {'ticket': ticket,
                   'form': form,
                   'user': user,
                   'level': level,
                   'handler': handler,
                   'topic': topic,
                   'username': mark_safe(json.dumps(user.username)),
                   'fullname': mark_safe(json.dumps(user.fullname)),
                   'admin': mark_safe(json.dumps(admin.username)),
                   'noti_noti': user.noti_noti,
                   'noti_chat': user.noti_chat,
                   }
        if request.method == 'POST':
            if 'tkid' in request.POST:
                ticket = Tickets.objects.get(id=request.POST['tkid'])
                ticket.status = 3
                ticket.save()
                TicketLog.objects.create(userid=user,
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
                                                 to=[rc.email],)
                            # email.send()
                            thread = EmailThread(email)
                            thread.start()
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
                    ticket.title = form.cleaned_data['title']
                    ticket.content = form.cleaned_data['content']
                    ticket.sender = user
                    ticket.topicid = Topics.objects.get(id=request.POST['topic'])
                    muc = int(request.POST['level'])
                    priority = LevelPriority.objects.get(id=muc)
                    ticket.priority = priority
                    time = priority.time
                    ticket.datestart = timezone.now()
                    ticket.dateend = (timezone.now() + timezone.timedelta(seconds=time))
                    # if request.POST['level'] == '0':
                    #     ticket.dateend = (timezone.now() + timezone.timedelta(minutes=Level_0))
                    # elif request.POST['level'] == '1':
                    #     ticket.dateend = (timezone.now() + timezone.timedelta(minutes=Level_1))
                    # else:
                    #     ticket.dateend = (timezone.now() + timezone.timedelta(minutes=Level_2))
                    if request.FILES.get('attach') is not None:
                        if request.FILES['attach']._size < MAX_UPLOAD_SIZE:
                            ticket.attach = request.FILES['attach']
                            handle_uploaded_file(request.FILES['attach'])
                        else:
                            return render(request, 'user/home_user.html', content)
                    ticket.save()
                    TicketLog.objects.create(userid=user,
                                             ticketid=ticket,
                                             action='tạo mới yêu cầu',
                                             date=timezone.now().date(),
                                             time=timezone.now().time())
                    # if topicA.type_send == 1:
                    #     for rc in receiver:
                    #         if rc.receive_email == 1:
                    #             email = EmailMessage('New ticket',
                    #                                 render_to_string('user/new_ticket.html', {}),
                    #                                 to=[rc.email],)
                    #             email.send()
                    # else:
                    #     email = EmailMessage('New ticket',
                    #                         render_to_string('user/new_ticket.html', {}),
                    #                         to=[admin.email],)
                    #     email.send()
                return redirect("/user")
            
        return render(request, 'user/home_user.html', content)
    else:
        return redirect("/")


def user_data(request):
    if request.session.has_key('user') and (Users.objects.get(username=request.session['user'])).status == 1:
        user = Users.objects.get(username=request.session['user'])
        tk = Tickets.objects.filter(sender=user.id).order_by('-id')
        data = []
        for tk in tk:
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
                handler = '<p id="hd' + str(tk.id) + '">'
                for t in TicketAgent.objects.filter(ticketid=tk.id):
                    handler += t.agentid.username + "<br>"
                handler += '</p>'
            id = '''<button type="button" class="btn" data-toggle="modal" data-target="#'''+str(tk.id)+'''content">'''+str(tk.id)+'''</button>'''
            option = ''
            if tk.status < 3:
                option += '''<button type="button" class="btn btn-danger close_ticket" data-toggle="tooltip" title="đóng" id="'''+str(tk.id)+'''" ><span class="glyphicon glyphicon-off"></span></button>'''
            else:
                option += '''<button disabled type="button" class="btn btn-danger close_ticket" data-toggle="tooltip" title="đóng" id="'''+str(tk.id)+'''"><span class="glyphicon glyphicon-off"></span></button>'''
            if 1 == tk.status or tk.status == 2:
                option += '''<a href='javascript:register_popup("chat'''+str(tk.id)+'''", '''+str(tk.id)+''');' type="button" class="btn btn-primary" data-toggle="tooltip" title="trò chuyện" id="chat_with_agent"><span class="glyphicon glyphicon-comment" ></span><input type="hidden" value="'''+str(tk.id)+'''"/></a>'''
            else:
                option += '''<a  type="button" disabled class="btn btn-primary not-active" data-toggle="tooltip" title="trò chuyện"><span class="glyphicon glyphicon-comment" ></span></a>'''
            option += '''<a type="button" target=_blank class="btn btn-warning" href="/user/history_'''+str(tk.id)+ '''" data-toggle="tooltip" title="dòng thời gian"><i class="fa fa-history"></i></a>'''
            # if tk.lv_priority == 0:
            #     level = r'<span class ="label label-success"> Thấp </span>'
            # elif tk.lv_priority == 1:
            #     level = r'<span class ="label label-warning"> Trung bình </span>'
            # else:
            #     level = r'<span class ="label label-danger"> Cao </span>'
            # if tk.expired == 1:
            #     status += r'<br><span class ="label label-danger"> Quá hạn </span>'
            downtime = '''<p class="downtime" id="downtime-'''+str(tk.id)+'''"></p>'''
            datestart = tk.datestart + timezone.timedelta(hours=7)
            data.append([id, tk.topicid.name, tk.title, str(datestart)[:-16], tk.priority.name, downtime, status, handler, option])
        ticket = {"data": data}
        tickets = json.loads(json.dumps(ticket))
        return JsonResponse(tickets, safe=False)


def handle_uploaded_file(f):
    # path = settings.MEDIA_ROOT+"/photos/"+f.name
    path = "media/photos/" + f.name
    file = open(path, 'wb+')
    for chunk in f.chunks():
        file.write(chunk)
    file.close()


def detail_user(request):
    if request.session.has_key('user')and (Users.objects.get(username=request.session['user'])).status == 1:
        user = Users.objects.get(username=request.session['user'])
        if request.method == 'POST':
            if 'change_user' in request.POST:
                u = Users.objects.get(id=request.POST['userid'])
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
                u = Users.objects.get(id=request.POST['userid'])
                u.password = request.POST['pwd']
                u.save()
            elif 'noti_noti' in request.POST:
                user.noti_noti = 0
                user.save()
            elif 'noti_chat' in request.POST:
                user.noti_chat = 0
                user.save()
        return render(request, 'user/detail_user.html', {'user': user, 'username': mark_safe(json.dumps(user.username)),'fullname': mark_safe(json.dumps(user.fullname)), 'noti_noti': user.noti_noti, 'noti_chat': user.noti_chat})
    else:
        return redirect("/")


def login_user(request):
    mess_resetpwd_error = 'Email chưa đăng ký hoặc không hợp lệ'
    mess_resetpwd_ok = 'Hãy kiểm tra email của bạn để cập nhật lại mật khẩu'
    mess_register_error = 'Thông tin đăng ký không hợp lý'
    mess_register_ok = 'Hãy kiểm tra email của bạn để hoàn tất đăng ký'
    mess_login_error = 'Đăng nhập thất bại'
    if request.session.has_key('user')and (Users.objects.get(username=request.session['user'])).status == 1:
        return redirect("/user")
    elif request.session.has_key('agent')and(Agents.objects.get(username=request.session['agent'])).status == 1:
        return redirect('/agent')
    elif request.session.has_key('admin'):
        return redirect('/agent/admin')
    elif request.session.has_key('leader'):
        return redirect('/agent/leader')
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
                        # 'domain': "113.190.232.90:8892",
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    # email.send()
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_error, 'error': error})
            elif 'aemail' in request.POST:
                form = AgentResetForm(request.POST)
                if form.is_valid():
                    to_email = form.cleaned_data['aemail']
                    current_site = get_current_site(request)
                    user = get_agent_email(to_email)
                    mail_subject = 'Reset password your account.'
                    message = render_to_string('user/agresetpwd.html', {
                        'user': user,
                        'domain': current_site.domain,
                        # 'domain': "113.190.232.90:8892",
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token1.make_token(user),
                    })
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    # email.send()
                    thread = EmailThread(email)
                    thread.start()
                    return render(request, 'user/index.html', {'mess': mess_resetpwd_ok})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html',{'mess': mess_resetpwd_error, 'error':error})
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
                        # 'domain': "113.190.232.90:8892",
                        'uid':urlsafe_base64_encode(force_bytes(user.id)).decode(),
                        'token':account_activation_token.make_token(user),
                    })
                    to_email = form.cleaned_data['email']
                    email = EmailMessage(
                                mail_subject, message, to=[to_email]
                    )
                    # email.send()
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
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 1:
                        agent = get_agent(agentname)
                        request.session['admin'] = agentname
                        return redirect('/agent/admin')
                        # mail_subject = 'Mã xác thực đăng nhập.'
                        # code = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
                        # dic[agent.username] = code
                        # now = datetime.datetime.now()
                        # expiry_date = now + datetime.timedelta(minutes=1)
                        # dic_time[code] = expiry_date
                        # message = render_to_string('user/confirm_admin.html', {'agent': agent, 'code': code})
                        # to_email = agent.email
                        # email = EmailMessage(
                        #             mail_subject, message, to=[to_email]
                        # )
                        # email.send()
                        # return redirect('/submitadmin')
                    elif authenticate_agent(agentname=agentname, agentpass=agentpass) == 0:
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
                            return redirect('/agent/leader')
                        else:
                            return render(request, 'user/index.html', {'mess': 'your account has been blocked'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_login_error,'error':error})
            # User đăng nhập
            else:
                form = UserLoginForm(request.POST)
                if form.is_valid():
                    username = request.POST['username']
                    request.session['user'] = username
                    return redirect("/user/")
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'user/index.html', {'mess': mess_login_error, 'error': error})
        return render(request, 'user/index.html', {})


def logout_user(request):
    del request.session['user']
    return redirect("/")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Users.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.status = 1
        user.save()
        return redirect('/')
    else:
        return HttpResponse('Đường dẫn không hợp lệ!')


def resetpwd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = Users.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetForm(request.POST)
            if form.is_valid():
                user.password = form.cleaned_data
                user.save()
                return redirect('/')
            else:
                return redirect('/')
        return render(request, 'user/formresetpass.html', {})
    else:
        return HttpResponse('Đường dẫn không hợp lệ!!')


def agresetpwd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        ag = Agents.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError, Agents.DoesNotExist):
        ag = None
    if ag is not None and account_activation_token1.check_token(ag, token):
        if request.method == 'POST':
            form = ResetForm(request.POST)
            if form.is_valid():
                ag.password = form.cleaned_data
                ag.save()
                return redirect('/')
            else:
                return redirect('/')
        return render(request, 'user/formresetpass.html', {})
    else:
        return HttpResponse('Đường dẫn kích hoạt không hợp lệ!')


def submitadmin(request):
    mess = 'Please confirm your email address to complete the login admin'
    mess_code_error = 'Code is incorrect'
    mess_time_error = 'Code was expired'
    if request.method == 'POST':
        if request.POST['code'] in dic.values():
            if datetime.datetime.now() < dic_time[request.POST['code']]:
                for agentname, code in dic.items():
                    if code == request.POST['code']:
                        request.session['admin'] = agentname
                        return redirect('/agent/admin')
            else:
                return render(request, 'user/submit_code_admin.html', {'mess': mess_time_error})
        else:
            return render(request, 'user/submit_code_admin.html', {'mess': mess_code_error})
    return render(request, 'user/submit_code_admin.html', {'mess': mess})
