from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
import uuid
import random

from django.utils.safestring import mark_safe
import json
from django.contrib.auth.models import User
import threading
from superadmin.forms import UserForm, authenticate, UserResetForm, get_user_email, ResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from superadmin.models import MyUser

from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
# from glanceclient import Client
from neutronclient.v2_0 import client as client_neutron #dòng này có nghĩa là thay tên cho "client" cần được import vào để tránh trùng với dùng thứ 3

loader = loading.get_plugin_loader('password')

# xác thực kết nối tới Controller
auth = loader.load_from_options(auth_url="http://192.168.40.146:5000/v3", username="admin", password="ok123", project_name="admin", user_domain_id="default", project_domain_id="default")

# tạo phiên kết nối
sess = session.Session(auth=auth)

# tạo các class add session và version
nova = client.Client(2, session=sess)
# glance = Client('2', session=sess)
neutron = client_neutron.Client(session=sess)
networks = neutron.list_networks()
network_list = []
for item in networks["networks"]:
    network_keys = {'name'}
    network_dict = {key: value for key, value in item.items() if key in network_keys}
    network_list.append(network_dict)

im = nova.glance.list()
image_list = []
for image in im:
    image_list.append(image.name)


sv = nova.servers.list()
sv_list = []
for item in sv:
    sv_list.append(item.name)

fl = nova.flavors.list()
flavor_list = []
for flavor in fl:
    combo = []
    combo = [flavor.ram, flavor.vcpus, flavor.disk]
    flavor_list.append(combo)
                
class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()

class CreateVmThread(threading.Thread):
    def __init__(self, svname, flavor=None, image=None, network_id=None, ram=None, vcpus=None, disk=None):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.svname = svname
        self.flavor = flavor
        self.image = image
        self.network_id = network_id
        self.ram = ram
        self.vcpus = vcpus
        self.disk = disk
        self.nova = client.Client(2, session=sess)

    def run(self):
        self.nova.servers.create(self.svname, flavor=self.flavor, image=self.image, nics = [{'net-id':self.network_id}],)
    def createFlavor(self):
        self.nova.flavors.create(self.svname, self.ram, self.vcpus, self.disk, flavorid='auto', ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True, description=None)

def home(request):
    user = request.user
    for item in sv:
        print(item._info)
        print(item._info['status'])
    if user.is_authenticated:
        if request.method == 'POST':
            svname = request.POST['svname']
            image = request.POST['image']
            network = request.POST['network']
            ram = int(float(request.POST['ram']) * 1024)
            vcpus = int(request.POST['vcpus'])
            disk = int(request.POST['disk'])
            if [ram, vcpus, disk] in flavor_list:
                fl = nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk)
                im = nova.glance.find_image(image)
                net = nova.neutron.find_network(network).id
                thread = CreateVmThread(svname=svname, flavor=fl, image=im, network_id=net)
                thread.start()
            else:
                thread = CreateVmThread(svname=svname, ram=ram, vcpus=vcpus, disk=disk)
                thread.createFlavor()
                check = False
                while check == False:
                    if nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk):
                        check = True
                        falvor = nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk)
                thread = CreateVmThread(svname, falvor, nova.glance.find_image(image), nova.neutron.find_network(network).id)
                thread.start()
        return render(request, 'kvmvdi/index.html',{'username': mark_safe(json.dumps(user.username)),
                                                        'networks': network_list,
                                                        'images': image_list})
    else:
        return HttpResponseRedirect('/')


def user_login(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'kvmvdi/index.html',{'username': mark_safe(json.dumps(user.username)),})
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
                    message = render_to_string('kvmvdi/resetpwd.html', {
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
                    return render(request, 'kvmvdi/login.html', {'mess': 'Please check email to reset your password!'})
                else:
                    error = ''
                    for field in form:
                        error += field.errors
                    return render(request, 'kvmvdi/login.html', {'error': error})
            elif 'agentname' and 'agentpass' in request.POST:
                username = request.POST['agentname']
                password = request.POST['agentpass']
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active and user.is_adminkvm:
                        login(request, user)
                        return HttpResponseRedirect('/home')
                    else:
                        return render(request, 'kvmvdi/login.html',{'error':'Your account is blocked!'})
                else:
                    return render(request, 'kvmvdi/login.html',{'error':'Invalid username or password '})
            elif 'firstname' and 'email' and 'password2' in request.POST:
                user_form = UserForm(request.POST)
                if user_form.is_valid():
                    user = user_form.save()
                    return redirect('/')
                else:
                    print(user_form.errors)
                    error = ''
                    for field in user_form:
                        error += field.errors
                    return render(request, 'kvmvdi/login.html',{'error':error})
        return render(request, 'kvmvdi/login.html')


def resetpwd(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = MyUser.objects.get(id=uid)
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data)
                user.save()
                return redirect('/')
            else:
                return redirect('/')
        return render(request, 'kvmvdi/formresetpass.html', {})
    else:
        return HttpResponse('Link is invalid!')

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_profile(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'kvmvdi/profile.html', {'username': mark_safe(json.dumps(user.username))})
    else:
        return HttpResponseRedirect('/')
    
