from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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
from superadmin.models import MyUser, Ops
import os


from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
# from glanceclient import Client
from neutronclient.v2_0 import client as client_neutron #dòng này có nghĩa là thay tên cho "client" cần được import vào để tránh trùng với dùng thứ 3

loader = loading.get_plugin_loader('password')
                
class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()

class VmThread(threading.Thread):
    def __init__(self, auth_url, username, password, project_name, user_domain_id, project_domain_id):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.auth = loader.load_from_options(auth_url=auth_url, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
        self.sess = session.Session(auth=self.auth)
        self.nova = client.Client(2, session=self.sess)
        self.neutron = client_neutron.Client(session=self.sess)

    def run(self, svname, flavor, image, network_id):
        self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}])

    def createFlavor(self, svname, ram, vcpus, disk):
        self.nova.flavors.create(svname, ram, vcpus, disk, flavorid='auto', ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True, description=None)

    def delete_vm(self, svid):
        self.nova.servers.delete(svid)
    
    def list_flavor(self):
        fl = self.nova.flavors.list()
        flavor_list = []
        for flavor in fl:
            combo = []
            combo = [flavor.ram, flavor.vcpus, flavor.disk]
            flavor_list.append(combo)
        return flavor_list

    def list_server(self):
        return self.nova.servers.list()

    def list_images(self):
        image_list = []
        for image in self.nova.glance.list():
            image_list.append(image.name)
        image_list.insert(0, "image_list")
        return image_list        

    def list_networks(self):
        network_list = []
        for item in self.neutron.list_networks()["networks"]:
            network_keys = {'name'}
            for key, value in item.items():
                if key in network_keys:
                    network_list.append(value)
        network_list.insert(0, "network_list")
        return network_list

    
    def find_flavor(self, ram=None, vcpus=None, disk=None, id=None):
        if id is None:
            return self.nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk)
        else:
            return self.nova.flavors.find(id=id)
    
    def find_image(self, image):
        return self.nova.glance.find_image(image)

    def find_network(self, network):
        return self.nova.neutron.find_network(network).id

class check_ping(threading.Thread):
    def __init__(self, host):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.host = host

    def run(self):
        response = os.system("ping -c 1 " + self.host)
        if response == 0:
            return True
        else:
            return False

def home(request):
    user = request.user
    list_ops = Ops.objects.all()
    if user.is_authenticated:
        if request.method == 'POST':
            if 'image' in request.POST:
                if Ops.objects.get(ip=request.POST['ops']):
                    ops = Ops.objects.get(ip=request.POST['ops'])
                    auth_url = "http://"+ops.ip+":5000/v3"
                    username = ops.username
                    password = ops.password
                    project_name = ops.project
                    user_domain_id = ops.userdomain
                    project_domain_id = ops.projectdomain

                    svname = request.POST['svname']
                    image = request.POST['image']
                    network = request.POST['network']
                    ram = int(float(request.POST['ram']) * 1024)
                    vcpus = int(request.POST['vcpus'])
                    disk = int(request.POST['disk'])

                    thread = VmThread(auth_url=auth_url, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
                    if [ram, vcpus, disk] in thread.list_flavor():
                        fl = thread.find_flavor(ram=ram, vcpus=vcpus, disk=disk)
                        im = thread.find_image(image)
                        net = thread.find_network(network)
                        thread.run(svname=svname, flavor=fl, image=im, network_id=net)
                    else:
                        thread.createFlavor(svname=svname, ram=ram, vcpus=vcpus, disk=disk)
                        check = False
                        while check == False:
                            if thread.find_flavor(ram=ram, vcpus=vcpus, disk=disk):
                                check = True
                        thread.run(svname=svname, flavor=thread.find_flavor(ram=ram, vcpus=vcpus, disk=disk), image=thread.find_image(image), network_id=thread.find_network(network))
                else:
                    return HttpResponseRedirect('/')
            elif 'delete' in request.POST:
                ops = Ops.objects.get(ip=request.POST['ops'])
                auth_url = "http://"+ops.ip+":5000/v3"
                username = ops.username
                password = ops.password
                project_name = ops.project
                user_domain_id = ops.userdomain
                project_domain_id = ops.projectdomain
                svid = request.POST['delete']
                thread = VmThread(auth_url=auth_url, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
                thread.delete_vm(svid=svid)
            elif 'ipsv' in request.POST:
                Ops.objects.create(name=request.POST['nameops'],
                                    ip=request.POST['ipsv'],
                                    username=request.POST['username'],
                                    password=request.POST['password'],
                                    project=request.POST['project'],
                                    userdomain=request.POST['userid'],
                                    projectdomain=request.POST['projectid'])
        return render(request, 'kvmvdi/index.html',{'username': mark_safe(json.dumps(user.username)),
                                                        'ops': list_ops})
    else:
        return HttpResponseRedirect('/')

def home_data(request, ops_ip):
    user = request.user
    if user.is_authenticated:
        if Ops.objects.get(ip=ops_ip):
            thread = check_ping(host=ops_ip)
            if thread.run():
                ops = Ops.objects.get(ip=ops_ip)
                auth_url = "http://"+ops.ip+":5000/v3"
                username = ops.username
                password = ops.password
                project_name = ops.project
                user_domain_id = ops.userdomain
                project_domain_id = ops.projectdomain

                thread = VmThread(auth_url=auth_url, username=username, password=password, project_name=project_name, user_domain_id=user_domain_id, project_domain_id=project_domain_id)
                # print(thread.list_networks())
                data = []
                for item in thread.list_server():
                    # print(dir(item))
                    # print(item.interface_list())
                    try:
                        host = '<p>'+item._info['OS-EXT-SRV-ATTR:host']+'</p>'
                    except:
                        host = '<p></p>'
                    try:
                        name = '<p>'+item._info['name']+'</p>'
                    except:
                        name = '<p></p>'

                    try:
                        image_name = '<p>'+thread.find_image(image=item._info['image']['id']).name+'</p>'
                    except:
                        image_name = '<p></p>'

                    try:
                        ip = '<p>'+next(iter(item.networks.values()))[0]+'</p>'
                    except:
                        ip = '<p></p>'

                    try:
                        network = '<p>'+list(item.networks.keys())[0]+'</p>'
                    except:
                        network = '<p></p>'

                    try:
                        flavor = '<p>'+thread.find_flavor(id=item._info['flavor']['id']).name+'</p>'
                    except:
                        flavor = '<p></p>'

                    if item._info['status'] == 'ACTIVE':
                        status = '<span class="label label-success">'+item._info['status']+'</span>'
                    else:
                        status = '<span class="label label-danger">'+item._info['status']+'</span>'

                    created = '<p>'+item._info['created']+'</p>'

                    try:
                        actions = '''
                        <div class="btn-group">
                            <button type="button" class="btn btn-danger delete" name="'''+ops_ip+'''" id="del_'''+item._info['id']+'''">
                                <i class="fa fa-trash" data-toggle="tooltip" title="Delete"></i>
                            </button>
                            <button type="button" class="btn btn-success console" data-title="console" id="'''+item.get_console_url("novnc")["console"]["url"]+'''">
                                <i class="fa fa-bars" data-toggle="tooltip" title="Console"></i>
                            </button> 
                        </div>
                        '''
                    except:
                        actions = '''
                        <div class="btn-group">
                            <button type="button" class="btn btn-danger delete" name="'''+ops_ip+'''" id="del_'''+item._info['id']+'''">
                                <i class="fa fa-trash" data-toggle="tooltip" title="Delete"></i>
                            </button>
                        </div>
                        '''
                    data.append([host, name, image_name, ip, network, flavor, status, created, actions])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)
            else:
                data = []
                data.append(['<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>', '<p></p>'])
                big_data = {"data": data}
                json_data = json.loads(json.dumps(big_data))
                return JsonResponse(json_data)

            

def user_login(request):
    user = request.user
    if user.is_authenticated:
        return HttpResponseRedirect('/home')
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
    
