from django.contrib.auth.models import User
from django.test import TestCase, Client

from typing import NamedTuple


class TemplateUrlTuple(NamedTuple):
    template: str
    address: str


USER_NAME = 'NoName'

SIGNUP_PAGE = TemplateUrlTuple('users/signup.html', '/auth/signup/')
LOGIN_PAGE = TemplateUrlTuple('users/login.html', '/auth/login/')
LOGGED_OUT_PAGE = TemplateUrlTuple('users/logged_out.html', '/auth/logout/')
PASS_RESET_CONFIRM_PAGE = TemplateUrlTuple('users/password_reset_confirm.html',
                                           '/auth/reset/uidb64/token/')
PASS_RESET_COMPLETE_PAGE = TemplateUrlTuple(
    'users/password_reset_complete.html',
    '/auth/reset/done/')

PASS_CHANGE_FORM = TemplateUrlTuple('users/password_change_form.html',
                                    '/auth/password_change/')
PASS_CHANGE_DONE = TemplateUrlTuple('users/password_change_done.html',
                                    '/auth/password_change/done/')
PASS_RESET_FORM = TemplateUrlTuple('users/password_reset_form.html',
                                   '/auth/password_reset/')
PASS_RESET_DONE = TemplateUrlTuple('users/password_reset_done.html',
                                   '/auth/password_reset/done/')


class UserUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        #  authorized
        cls.user_logged = User.objects.create_user(username=USER_NAME)
        cls.logged_client = Client()
        cls.logged_client.force_login(cls.user_logged)

    def test_not_authorized_urls(self):
        """Check login,signup, password reset urls for guests"""
        pages = [SIGNUP_PAGE,
                 LOGIN_PAGE,
                 LOGGED_OUT_PAGE,
                 PASS_RESET_CONFIRM_PAGE,
                 PASS_RESET_COMPLETE_PAGE]
        for template, address in pages:
            with self.subTest(address=address):
                guest_response = self.logged_client.get(address)
                self.assertTemplateUsed(guest_response, template)

    def test_authorized_urls(self):
        """Check password change urls for logged users"""
        pages = [PASS_CHANGE_FORM,
                 PASS_CHANGE_DONE,
                 PASS_RESET_FORM,
                 PASS_RESET_DONE]
        for template, address in pages:
            with self.subTest(address=address):
                logged_response = self.logged_client.get(address)
                self.assertTemplateUsed(logged_response, template)
