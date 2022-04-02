from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from blog.models import Post
from datetime import datetime
from django.db.models import Q
from django.contrib.sites.models import Site
from django.contrib.auth import login

from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.views import LoginView, LogoutView

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import LoggedRecord
from .tokens import account_activation_token
from django.views.generic import View
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from tracking_analyzer.models import Tracker


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']

            new_user = form.save(commit=False)
            # deactivate the account till it is confirmed
            new_user.is_active = False
            new_user.save()
            subject = 'Activate your We Too Write Account'
            # shortcut to render html
            message = render_to_string('member/account_activation_email.html', {
                'user': new_user,
                'domain': Site.objects.get_current().domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user)
            })
            new_user.email_user(subject, message)
            messages.success(request, f'{first_name.capitalize()} an email has been sent on {new_user.email} by the Admin with your '
                                      f'registration confirmation link.'
                                      f' Please click on it to activate your registration and login')
            return render(request, 'member/conf_regn.html')
    else:
        form = UserRegisterForm()
    return render(request, 'member/member-register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        print(u_form, p_form)
        if u_form.is_valid() and p_form.is_valid():
            print(u_form, p_form, 'valid')
            u_form.save()
            p_form.save()
            messages.success(request, f'Your profile has been updated!')
            return redirect('blog-home')

    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'member/profile.html', context)


def check_name(request):
    users = User.objects.all()
    f_name = request.GET.get('search_term')
    f_email = request.GET.get('search_email')
    print(f_email)
    names = []
    emails = []
    checked_name = {}
    checked_email = {}
    for user in users:
        name = user.username
        email = user.email
        names.append(name)
        emails.append(email)
        if f_name in names or f_email in emails:
            checked_name['data'] = 'Taken'
            checked_name['email_data'] = 'Taken'
            return JsonResponse(checked_name)
    checked_name['data'] = 'Available'
    checked_name['email_data'] = 'Available'
    return JsonResponse(checked_name)


class Login(LoginView):
    template_name = 'member/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blog-home')
        else:

            return render(request, 'member/login.html')

    def get_success_url(self):
        return super().get_success_url()


def email_confirm(request):
    f_email = request.GET.get('search_email')
    user = User.objects.filter(email__contains=f_email)
    if user:
        response = {'data': 'Available'}
        return JsonResponse(response)
    response = {'data': 'notAvailable'}
    return JsonResponse(response)


def activate(request, uidb64, token, ):
    print('activating')
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError):
        user = None
        # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # set user is active true
        user.is_active = True
        user.save()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print('activated')
        messages.success(request, f'Congrats {user.username.capitalize()}! Your account is active now!')

        return redirect('blog-home')
    else:
        messages.warning(request, f'The confirmation link was invalid, possibly because it has already been used.'
                                  f' Register again')
        return render(request, 'member/member-register.html')
