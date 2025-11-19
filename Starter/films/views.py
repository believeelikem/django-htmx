from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model

from films.forms import RegisterForm

# Create your views here.
class IndexView(TemplateView):
    template_name = 'index.html'
    
class Login(LoginView):
    template_name = 'registration/login.html'


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()  # save the user
        return super().form_valid(form)
    
    
from django.contrib.auth import get_user_model
import re
    
def check_username(request):
    username = request.POST.get("username")
    content_ = None
    if get_user_model().objects.filter(username = username).exists():
        content = "This username already exists"
    elif re.search(r'\s+',username):
        content = "Enter a valid name,not spaces"
    elif not username:
        content = "Enter a name"
    else:
        print("Got here ")
        content_= "✅ username is available"
               
    if content_:
        return HttpResponse(f"<div style = 'color:green;' id='username-error' class='success' > {content_} </div>")
    
    return HttpResponse(f"<div style = 'color:red;' id='username-error' class='error'> {content} </div>")