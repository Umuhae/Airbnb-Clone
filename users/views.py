import os, requests

from django.http import HttpResponse
from django.utils import translation
from django.contrib.auth.views import PasswordChangeView
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView, UpdateView
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from . import forms, models, mixins
from django.contrib.messages.views import SuccessMessageMixin
# class LoginView(View):
#
#     def get(self, request):
#         form = forms.LoginForm()
#         return render(request, "users/login.html", {"form": form})
#
#     def post(self, request):
#         form = forms.LoginForm(request.POST)
#         print(form.is_valid())
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             password = form.cleaned_data.get('password')
#             print(email, password)
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect(reverse('core:home'))
#         else:
#             print(form, 'invalie')
#         return render(request, "users/login.html", {"form": form})

class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    # success_url = reverse_lazy("core:home")
    initial = {'email': 'ui706@naver.com'}

    def form_valid(self, form): #     if form.is_valid(): 이거 안해도됨
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get('next')
        if next_arg:
            return next_arg
        else:
            return reverse("core:home")
def log_out(request):
    messages.info(request, f"See you later")
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(mixins.LoggedOutOnlyView, FormView):
    template_name = "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    # initial = {
    #     "first_name": "Nico",
    #     "last_name": "serr",
    #     "email": "konlp@kakao.com",
    # }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.save()
        # to do: add success message
    except models.User.DoesNotExist:
        # to do: add error message
        pass
    return redirect(reverse("core:home"))


def github_login(request):
    client_id = os.environ.get('GH_ID')
    redirect_uri = 'http://127.0.0.1:8000/users/login/github/callback'
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}")


class GithubException(Exception):
    pass

def github_callback(request):
    try:
        client_id = os.environ.get('GH_ID')
        client_secret = os.environ.get('GH_SECRET')
        code = request.GET.get('code')#<QueryDict: {'code': ['6f5f07942dae243ed9a6']}>
        if code is not None:
            token_request = requests.post(f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secret}&code={code}",
                                    headers={"Accept": "application/json"})
            token_json = token_request.json()
            error = token_json.get('error', None)
            if error is not None:
                raise GithubException()
            else:
                access_token = token_json.get('access_token')
                profile_request = requests.get(f"https://api.github.com/user",
                                           headers={"Authorization": f"token {access_token}",
                                                    "Accept": "application/json"})
                profile_json = profile_request.json()

                username = profile_json.get('login', None)
                if username is not None:
                    name = profile_json.get('name', None)
                    email = profile_json.get('email', None)
                    bio = profile_json.get('bio', None)
                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException()
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                                email=username+'github.com',
                                first_name=username,
                                username=username,
                                bio=username,
                                login_method=models.User.LOGIN_GITHUB,
                                email_verified=True,)
                        user.set_unusable_password()
                        user.save()
                    login(request, user)
                    messages.success(request, f"Welcome back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException()
        else:
            raise GithubException()
    except GithubException:
        # sned error message
        messages.error(request, e)
        return redirect(reverse("users:login"))

def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code"
    )


class KakaoException(Exception):
    pass


def kakao_callback(request):
    try:
        code = request.GET.get("code")
        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        token_json = token_request.json()
        error = token_json.get("error", None)
        if error is not None:
            raise KakaoException()
        access_token = token_json.get("access_token")
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}",
                     "Content-type":"application/x-www-form-urlencoded;charset=utf-8"},
        )
        profile_json = profile_request.json()
        print(profile_json)
        nickname = profile_json.get('properties', None).get('nickname')
        kakao_account = profile_json.get("kakao_account", None)
        profile_json = kakao_account.get("profile", None)
        profile_image = profile_json.get('profile_image_url', None)
        email = kakao_account.get('email',None)
        if email is None:
            raise KakaoException()
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException()
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email=email,
                username=email,
                first_name=nickname,
                login_method=models.User.LOGIN_KAKAO,
                email_verified=True,
            )
            user.set_unusable_password()
            user.save()
            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f"{nickname}-avatar.png", ContentFile(photo_request.content))
        messages.success(request, f"Welcome back {user.first_name}")
        login(request, user)
        return redirect(reverse("core:home"))
    except KakaoException:
        messages.error(request, e)
        return redirect(reverse("users:login"))


class UserProfileView(DetailView):

    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    success_message = 'Profile Updated'

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birthdate"}
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        return form

class UpdatePasswordView(
    mixins.EmailLoginOnlyView,
    mixins.LoggedInOnlyView,
    SuccessMessageMixin,
    PasswordChangeView
):

    template_name = "users/update-password.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "Current password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "New password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "Confirm new password"
        }
        return form

    success_message = '비밀번호가 업데이트 되었습니다.'

    def get_success_url(self):
        return self.request.user.get_absolute_url()


def switch_language(request):
    lang = request.GET.get("lang", None)
    if lang is not None:
        request.session[translation.LANGUAGE_SESSION_KEY] = lang
    return HttpResponse(status=200)