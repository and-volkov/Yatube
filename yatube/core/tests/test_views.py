from django.contrib.auth.models import User
from django.test import TestCase, Client

from typing import NamedTuple


class CustomErrorTemplate(NamedTuple):
    error: str
    template: str


ERROR_404 = CustomErrorTemplate('404', 'core/404.html')
ERROR_403_CSRF = CustomErrorTemplate('403', 'core/403csrf.html')
ERROR_500 = CustomErrorTemplate('500', 'core/500html')

USER_NAME = 'NoName'


class CustomErrorPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username=USER_NAME)

    def setUp(self):
        self.guest_client = Client()
        self.user_client = Client()
        self.user_client.force_login(self.user)

