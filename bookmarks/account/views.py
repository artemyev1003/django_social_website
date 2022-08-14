from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views import View
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm, CustomAuthenticationForm
from .models import Profile


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


class RegisterView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request,
                      'registration/register.html',
                      {'user_form': user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)

            # Pass the new user's name as a GET parameter:
            # base_url = reverse('account:register_success')
            # query_string = urlencode({'name': new_user.first_name})
            # url = f'{base_url}?{query_string}'
            name = new_user.first_name
            return redirect(reverse('account:register_success', args=[name]))
        return render(request,
                      'registration/register.html',
                      {'user_form': user_form})


def register_success(request, name):
    # name = request.GET.get('name')
    return render(request,
                  'registration/register_done.html',
                  {'new_user': name})


# @method_decorator(login_required, name='get')
# @method_decorator(login_required, name='post')
class ProfileUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request,
                      'account/update.html',
                      {'user_form': user_form,
                       'profile_form': profile_form})

    def post(self, request):
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Error occurred while updating your profile')
        return render(request,
                      'account/update.html',
                      {'user_form': user_form,
                       'profile_form': profile_form})
