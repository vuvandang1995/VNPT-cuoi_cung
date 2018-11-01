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
from .forms import *


class EmailThread(threading.Thread):
    def __init__(self, email):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.email = email

    def run(self):
        self.email.send()

def home(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'videochat/home.html',{'username': mark_safe(json.dumps(user.username)),})
    else:
        return HttpResponseRedirect('/')


def user_login(request):
    user = request.user
    if user.is_authenticated:
        return render(request, 'videochat/home.html',{'username': mark_safe(json.dumps(user.username)),})
    else:
        if request.method == 'POST':
            if 'agentname' and 'agentpass' in request.POST:
                username = request.POST['agentname']
                password = request.POST['agentpass']
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect('/home')
                    else:
                        return HttpResponse("Your WebRTC account is disabled.")
                else:
                    print("Invalid login details: {0}, {1}".format(username, password))
                    return HttpResponse("Invalid login details supplied. <a href='/'>Please try again</a>")
            elif 'firstname' and 'email' and 'password2' in request.POST:
                user_form = UserForm(request.POST)
                if user_form.is_valid():
                    user = user_form.save()
                    return redirect('/')
                else:
                    print(user_form.errors)
        return render(request, 'videochat/login.html')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def user_profile(request):
    user = request.user
    return render(request, 'videochat/profile.html', {'username': mark_safe(json.dumps(user.username))})