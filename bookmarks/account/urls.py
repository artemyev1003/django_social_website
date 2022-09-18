from django.urls import path, reverse_lazy
from django.contrib.auth.views import (LogoutView,
                                       PasswordChangeView, PasswordChangeDoneView,
                                       PasswordResetView, PasswordResetDoneView,
                                       PasswordResetConfirmView, PasswordResetCompleteView,
                                       )
from .views import (dashboard, RegisterView, register_success,
                    ProfileUpdateView, CustomLoginView, user_list, user_detail,
                    user_follow)

app_name = 'account'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('password_change/',
         PasswordChangeView.as_view(success_url=reverse_lazy('account:password_change_done')),
         name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(),
         name='password_change_done'),
    path('password_reset/',
         PasswordResetView.as_view(success_url=reverse_lazy('account:password_reset_done')),
         name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(success_url=reverse_lazy('account:password_reset_complete')),
         name='password_reset_confirm'),
    path('reset/done/',
         PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/done/<str:name>/', register_success, name='register_success'),
    path('update/', ProfileUpdateView.as_view(), name='update'),
    path('users/', user_list, name='user_list'),
    path('users/follow', user_follow, name='user_follow'),
    path('users/<username>', user_detail, name='user_detail'),
]
