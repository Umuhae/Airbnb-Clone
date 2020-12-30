import uuid
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from core import managers as core_managers
# Create your models here.
class User(AbstractUser):
    """ 커스텀 유저 모델 """

    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'
    GENDER_OTHER = 'other'

    GENDER_CHOICES = (
        (GENDER_MALE, _("Male")),
        (GENDER_FEMALE, _("Female")),
        (GENDER_OTHER, _("Other")),
    )

    LANGUAGE_ENGLISH = 'en'
    LANGUAGE_KOREAN = 'kr'

    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, _("English")),
        (LANGUAGE_KOREAN, _("Korean")),
    )

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = 'github'
    LOGIN_KAKAO= 'kakao'

    LOGIN_CHOICES = ( (LOGIN_EMAIL, 'Email'),
                      (LOGIN_GITHUB, 'Github'),
                      (LOGIN_KAKAO, 'Kakao'),
                      )

    CURRENCY_USD = 'usd'
    CURRENCY_KRW = 'krw'
    CURRENCY_CHOICES = ((CURRENCY_USD, 'USD'), (CURRENCY_KRW, 'KRW'))
    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(
        _("gender"), choices=GENDER_CHOICES, max_length=10, blank=True
    )
    bio = models.TextField(_("bio"), blank=True)
    birthdate = models.DateField(blank=True, null=True)
    language = models.CharField(
        _("language"),
        choices=LANGUAGE_CHOICES,
        max_length=2,
        blank=True,
        default=LANGUAGE_KOREAN,
    )
    currency = models.CharField(choices=CURRENCY_CHOICES, max_length=3,  blank=True)
    superhost = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(max_length=120, default="",blank=True)
    login_method = models.CharField(max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL)
    objects = core_managers.CustomModelManager()
    def get_absolute_url(self):
        return reverse("users:profile", kwargs={'pk': self.pk})

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            html_message = f'Verify account, this is your secret: <a href="http://127.0.0.1:8000/users/verify/{secret}">here</a>'
            html_message = render_to_string("emails/verify_email.html", {'secret': secret})
            send_mail(_("Verify Airbnb Account"),
                    strip_tags(html_message),
                    settings.EMAIL_FROM,
                    [self.email],
                    fail_silently=False,
                    html_message = html_message,
                    )
            self.save()

        return