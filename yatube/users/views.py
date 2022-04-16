from django.views.generic import CreateView
from django.urls import reverse_lazy

from .forms import CreationForm, PassChangeForm, PassResetForm, PassSetForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(CreateView):
    form_class = PassChangeForm
    template_name = 'auth/password_change_form.html'
    success_url = 'auth/password_change_done.html'


class PasswordReset(CreateView):
    form_class = PassResetForm
    template_name = 'auth/password_reset_form.html'
    success_url = 'auth/password_reset_done.html'


class PasswordSet(CreateView):
    form_class = PassSetForm
    template_name = 'auth/password_reset_confirm.html'
    success_url = 'auth/password_reset_complete'
