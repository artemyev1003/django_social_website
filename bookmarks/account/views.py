from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm, CustomAuthenticationForm
from .models import Profile, Contact
from actions.models import Action
from common.decorators import ajax_required
from actions.utils import create_action


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm

@login_required
def dashboard(request):
    # Display all actions by default
    actions = Action.objects.exclude(user=request.user)
    following_ids = request.user.following.values_list('id',
                                                       flat=True)
    if following_ids:
        # If user is following others, retrieve only their actions
        actions = actions.filter(user_id__in=following_ids)
    actions = actions.select_related('user', 'user__profile')[:10]
    return render(request, 'account/dashboard.html',
                  {'section': 'dashboard',
                   'actions': actions})


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
            create_action(new_user, 'has created an account')

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


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    return render(request,
                  'account/user/list.html',
                  {'section': 'people',
                   'users': users})


@login_required
def user_detail(request, username):
    user = get_object_or_404(User,
                             username=username,
                             is_active=True)
    return render(request,
                  'account/user/detail.html',
                  {'section': 'people',
                   'user': user})


@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
