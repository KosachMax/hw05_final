from django.views.generic import CreateView

from django.urls import reverse_lazy

from .forms import CreationForm

from django.shortcuts import redirect


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


class SignUP(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:main_page')
    template_name = 'users/signup.html'
