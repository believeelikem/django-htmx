from django.http.response import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.contrib.auth import get_user_model
from films.forms import RegisterForm
from .models import *
from django.views.generic import ListView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import get_max_order,reorder
from django.shortcuts import get_object_or_404

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

class FilmList(LoginRequiredMixin,ListView):
    template_name = "films.html"
    model = Film
    context_object_name = "films"
    
    def get_queryset(self):
        user = self.request.user
        return UserFilms.objects.filter(user = user)

@login_required
def add_film(request):
    name = request.POST.get("filmname")
    
    error = ''
    
    film = Film.objects.get_or_create(name = name)[0]          

    if not UserFilms.objects.filter(user = request.user,film = film).exists():
            UserFilms.objects.create(film = film, user = request.user, order = get_max_order(request.user))  
            messages.success(request,F"{name} added to films")  
    else:
        error = f" <span style = 'color:red;' >{name} already exists </span>"  
                     
    films = UserFilms.objects.filter(user = request.user)
    
    # return template with all of the users films
    return render(request,"partials/film-list.html",{"films":films,"error":error})


@login_required
@require_http_methods(["DELETE"])
def delete_film(request,pk):
    UserFilms.objects.get(pk=pk).delete()   
    reorder(request.user)
    films = UserFilms.objects.filter(user = request.user)
    return render(request,"partials/film-list.html",{"films":films})

def search_film(request):
    q = request.POST.get('search')
    
    
    results = Film.objects.filter(name__icontains = q).exclude(
        name__in = UserFilms.objects.filter(user = request.user).values_list('film__name',flat = True)
    )
    
    context = {
        "results":results
    }
    
    return render(request,"partials/search-results.html",context)

def clear(request):
    return HttpResponse("")

def sort(request):
    film_pks_order = request.POST.getlist("film_order")
    films = []
    for idx, film_pk in enumerate(film_pks_order,start=1):
        userfilm = UserFilms.objects.get(pk = film_pk)
        userfilm.order = idx
        userfilm.save()
        films.append(userfilm)
        
    return render(request, "partials/film-list.html",{"films":films})

@login_required
def detail(request,pk):
    user_film = get_object_or_404(UserFilms,pk = pk)
    context = {
        "userfilm":user_film
    }
    return render(request, "partials/film-detail.html", context)

def films_partial(request):
    return render(request,"partials/film-list.html",{'films':UserFilms.objects.filter(user = request.user)})